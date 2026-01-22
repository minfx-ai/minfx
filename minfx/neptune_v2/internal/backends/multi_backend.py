#
# Copyright (c) 2024, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""MultiBackend: Composite backend that fans out operations to multiple backends in parallel."""

from __future__ import annotations

__all__ = ["MultiBackend"]

import threading
import time
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FuturesTimeoutError,
    as_completed,
)
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Iterator,
    NoReturn,
)

from minfx.neptune_v2.exceptions import (
    AllBackendsFailedError,
    BackendError,
    NeptuneMultiBackendClosedError,
)
from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
from minfx.neptune_v2.internal.utils.logger import get_logger

if TYPE_CHECKING:
    from minfx.neptune_v2.common.exceptions import NeptuneException
    from minfx.neptune_v2.core.components.operation_storage import OperationStorage
    from minfx.neptune_v2.internal.backends.api_model import (
        ApiExperiment,
        Attribute,
    )
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import UniqueId
    from minfx.neptune_v2.internal.operation import Operation
    from minfx.neptune_v2.internal.utils.git import GitInfo

logger = get_logger()

# Constants
MAX_RETRY_TIMEOUT_SECONDS = 30
HEALTH_CHECK_INTERVAL_SECONDS = 60
MAX_PARALLEL_WORKERS = 10
FAILURE_THRESHOLD = 3  # Failures before marking as degraded


# =============================================================================
# Backend Health States (Rust-style discriminated union)
# =============================================================================
# Each state variant carries exactly the data relevant to that state.
# This prevents inconsistent states like "healthy with 5 failures".


@dataclass(frozen=True)
class Healthy:
    """Backend is operating normally."""

    last_success_time: float


@dataclass(frozen=True)
class Failing:
    """Backend has failed 1-2 times consecutively, still routable."""

    consecutive_failures: int  # 1 or 2
    last_error: Exception
    last_success_time: float  # Preserved from before failures


@dataclass(frozen=True)
class Degraded:
    """Backend has failed 3+ times, excluded from routing."""

    consecutive_failures: int  # >= 3
    last_error: Exception


# Union type: health is ONE of these
BackendHealth = Healthy | Failing | Degraded


def is_routable(health: BackendHealth) -> bool:
    """Check if backend should receive operations (Healthy or Failing)."""
    return isinstance(health, (Healthy, Failing))


# =============================================================================
# Backend State Container
# =============================================================================


@dataclass
class BackendState:
    """Tracks a single backend and its health state."""

    backend: NeptuneBackend
    index: int
    health: BackendHealth = field(default_factory=lambda: Healthy(last_success_time=time.time()))


# =============================================================================
# State Transitions (Pure Functions)
# =============================================================================


def compute_success_health() -> Healthy:
    """Compute new health state after successful operation."""
    return Healthy(last_success_time=time.time())


def compute_failure_health(current_health: BackendHealth, error: Exception) -> BackendHealth:
    """Compute new health state after failed operation.

    This is a pure function that computes the next state based on current state.
    Must be called while holding the lock to ensure atomic read-modify-write.
    """
    if isinstance(current_health, Healthy):
        # First failure: Healthy -> Failing(1)
        return Failing(
            consecutive_failures=1,
            last_error=error,
            last_success_time=current_health.last_success_time,
        )
    elif isinstance(current_health, Failing):
        n = current_health.consecutive_failures
        if n < FAILURE_THRESHOLD - 1:
            # Still under threshold: Failing(n) -> Failing(n+1)
            # With FAILURE_THRESHOLD=3, this matches n=1 only (n < 2)
            # When n=2, falls through to else branch -> Degraded(3)
            return Failing(
                consecutive_failures=n + 1,
                last_error=error,
                last_success_time=current_health.last_success_time,
            )
        else:
            # Hit threshold: Failing(2) -> Degraded(3)
            return Degraded(
                consecutive_failures=n + 1,
                last_error=error,
            )
    elif isinstance(current_health, Degraded):
        # Already degraded: increment counter
        return Degraded(
            consecutive_failures=current_health.consecutive_failures + 1,
            last_error=error,
        )
    # Should never reach here, but satisfy type checker
    return Degraded(consecutive_failures=1, last_error=error)


class MultiBackend(NeptuneBackend):
    """Composite backend that fans out operations to multiple backends in parallel.

    Thread Safety:
        This class is thread-safe. It uses an internal lock for state management
        and integrates with the container's RLock passed via set_container_lock().

        IMPORTANT: All state transitions are atomic - they read current state and
        compute new state while holding the lock. This prevents race conditions
        where concurrent failures could corrupt the consecutive_failures counter.

    Read Consistency:
        Read operations use first-available semantics. The first backend to respond
        successfully provides the result. This means reads may return slightly stale
        data if backends have different states (eventual consistency).
    """

    def __init__(self, backends: list[NeptuneBackend]) -> None:
        """Create MultiBackend with sequential indices (0, 1, 2, ...).

        For backends with custom indices (e.g., when some backends failed to connect),
        use from_indexed_backends() instead.
        """
        self._backend_states: list[BackendState] = [BackendState(backend=b, index=i) for i, b in enumerate(backends)]
        self._init_common(len(backends))

    @classmethod
    def from_indexed_backends(cls, indexed_backends: list[tuple[int, NeptuneBackend]]) -> MultiBackend:
        """Create MultiBackend with explicit indices.

        Use this when some backends failed to connect and you want to preserve
        the original numbering (e.g., if backend #1 fails, keep #0 and #2).

        Args:
            indexed_backends: List of (original_index, backend) tuples.
        """
        instance = object.__new__(cls)
        instance._backend_states = [BackendState(backend=b, index=idx) for idx, b in indexed_backends]
        instance._init_common(len(indexed_backends))
        return instance

    def _init_common(self, num_backends: int) -> None:
        """Common initialization for both constructors."""
        self._lock = threading.Lock()
        self._container_lock: threading.RLock | None = None
        self._shutdown_event = threading.Event()  # Thread-safe shutdown signaling
        self._executor = ThreadPoolExecutor(
            max_workers=min(num_backends, MAX_PARALLEL_WORKERS),
            thread_name_prefix="multi_backend",
        )
        self._health_check_timer: threading.Timer | None = None
        self._start_health_check_timer()

    def _check_not_closed(self) -> None:
        """Raise if backend has been closed.

        Must be called at the start of all public operation methods.
        """
        if self._shutdown_event.is_set():
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

    def iterate_backends(self) -> Iterator[NeptuneBackend]:
        """Yield all underlying backends.

        Used by MetadataContainer to register container workspace with each backend.
        """
        for state in self._backend_states:
            yield state.backend

    @property
    def _is_single_backend(self) -> bool:
        """Check if this MultiBackend wraps only a single backend."""
        return len(self._backend_states) == 1

    def _raise_all_failed(self, errors: list[BackendError]) -> NoReturn:
        """Raise appropriate exception based on backend count.

        For single-backend scenarios, re-raises the original exception to maintain
        backward compatibility with code that expects specific exception types.
        For multi-backend scenarios, raises AllBackendsFailedError.
        """
        if self._is_single_backend and len(errors) == 1:
            # Re-raise the original exception for backward compatibility
            raise errors[0].cause from None
        raise AllBackendsFailedError(errors)

    def set_container_lock(self, lock: threading.RLock) -> None:
        """Set the container's lock for coordinated synchronization.

        The container lock is used during sync() operations to ensure that:
        1. No new operations are submitted while syncing
        2. All backends complete their pending operations before sync returns

        Usage: The MetadataContainer acquires this lock before calling sync(),
        ensuring atomic sync across all backends.

        IMPORTANT: Must be called during initialization, before any operations
        are submitted. Calling this while operations are in-flight is undefined.
        """
        self._container_lock = lock

    def _start_health_check_timer(self) -> None:
        """Start periodic health check for degraded backends."""
        self._health_check_timer = threading.Timer(
            HEALTH_CHECK_INTERVAL_SECONDS,
            self._check_degraded_backends,
        )
        self._health_check_timer.daemon = True
        self._health_check_timer.start()

    def _check_degraded_backends(self) -> None:
        """Periodically check if degraded backends have recovered.

        Note: Requires NeptuneBackend to implement a health_ping() method for health checks.
        The health_ping() method should be a lightweight API call.

        Thread Safety: We snapshot degraded backend indices while holding the lock,
        then release the lock before calling health_ping() to avoid blocking other operations.
        Uses atomic transitions to ensure correct state updates.
        """
        if self._shutdown_event.is_set():
            return  # Don't check or reschedule during shutdown

        # Snapshot degraded backend indices and their backends (for ping)
        with self._lock:
            degraded_info = [
                (state.index, state.backend) for state in self._backend_states if isinstance(state.health, Degraded)
            ]

        # Ping outside the lock to avoid blocking other operations
        # Each backend is checked independently - one failure doesn't skip others
        for index, backend in degraded_info:
            backend_id = f"[backend {index}] ({backend.get_display_address()})"
            try:
                # Simple health check - requires NeptuneBackend.health_ping() method
                backend.health_ping()
                # Atomic transition: Degraded -> Healthy
                self._transition_on_success(index)
                logger.info(f"{backend_id} recovered")
            except Exception as e:
                # Note: We don't increment failure counter on ping failure
                # to avoid double-counting (ping is separate from operations)
                logger.info(
                    f"{backend_id} health check: still degraded ({e}). Will retry in {HEALTH_CHECK_INTERVAL_SECONDS}s"
                )

        # Reschedule only if not shutting down
        if not self._shutdown_event.is_set():
            self._start_health_check_timer()

    def _transition_on_success(self, index: int) -> None:
        """Atomically transition backend to Healthy state.

        Args:
            index: The original backend index (not position in list).

        Thread Safety: Reads current state and computes new state while holding lock.
        """
        with self._lock:
            pos = self._find_state_position(index)
            if pos is None:
                return  # Backend not found
            current = self._backend_states[pos]
            old_health = current.health
            new_health = compute_success_health()
            self._backend_states[pos] = BackendState(
                backend=current.backend,
                index=current.index,
                health=new_health,
            )

            # Log recovery transitions
            if isinstance(old_health, Failing):
                logger.info(f"{self._backend_id(index)} health: Failing -> Healthy (recovered)")
            elif isinstance(old_health, Degraded):
                logger.info(f"{self._backend_id(index)} health: Degraded -> Healthy (recovered)")

    def _transition_on_failure(self, index: int, error: Exception) -> None:
        """Atomically transition backend state on failure.

        Args:
            index: The original backend index (not position in list).

        Thread Safety: Reads current state and computes new state while holding lock.
        This ensures consecutive_failures counter is correctly incremented even with
        concurrent failures from multiple threads.
        """
        with self._lock:
            pos = self._find_state_position(index)
            if pos is None:
                return  # Backend not found
            current = self._backend_states[pos]
            old_health = current.health
            new_health = compute_failure_health(old_health, error)
            self._backend_states[pos] = BackendState(
                backend=current.backend,
                index=current.index,
                health=new_health,
            )

            # Log health state transitions
            if isinstance(old_health, Healthy) and isinstance(new_health, Failing):
                logger.warning(f"{self._backend_id(index)} health: Healthy -> Failing (first failure: {error})")
            elif isinstance(old_health, Failing) and isinstance(new_health, Failing):
                logger.warning(
                    f"{self._backend_id(index)} health: Failing -> Failing "
                    f"({new_health.consecutive_failures} consecutive failures)"
                )
            elif isinstance(old_health, Failing) and isinstance(new_health, Degraded):
                logger.warning(
                    f"{self._backend_id(index)} health: Failing -> Degraded "
                    f"({new_health.consecutive_failures} consecutive failures). "
                    f"Will retry in {HEALTH_CHECK_INTERVAL_SECONDS}s"
                )
            elif isinstance(old_health, Degraded) and isinstance(new_health, Degraded):
                logger.warning(
                    f"{self._backend_id(index)} health: Degraded -> Degraded "
                    f"({new_health.consecutive_failures} consecutive failures). "
                    f"Will retry in {HEALTH_CHECK_INTERVAL_SECONDS}s"
                )

    def _get_routable_backends(self) -> list[BackendState]:
        """Get backends that should receive operations.

        Returns Healthy and Failing backends, falling back to all if none routable.
        """
        with self._lock:
            routable = [s for s in self._backend_states if is_routable(s.health)]
            return routable if routable else list(self._backend_states)

    def _find_state_by_index(self, index: int) -> BackendState | None:
        """Find backend state by its original index."""
        for state in self._backend_states:
            if state.index == index:
                return state
        return None

    def _find_state_position(self, index: int) -> int | None:
        """Find the position in _backend_states for a given original index."""
        for pos, state in enumerate(self._backend_states):
            if state.index == index:
                return pos
        return None

    def _backend_id(self, index: int) -> str:
        """Format backend identifier including index and URL for logging."""
        state = self._find_state_by_index(index)
        if state:
            return f"[backend {index}] ({state.backend.get_display_address()})"
        return f"[backend {index}]"

    def _format_health_status(self, health: BackendHealth) -> str:
        """Format health state for logging."""
        if isinstance(health, Healthy):
            return "healthy"
        elif isinstance(health, Failing):
            return f"failing, {health.consecutive_failures} errors"
        elif isinstance(health, Degraded):
            return f"degraded, {health.consecutive_failures} errors"
        return "unknown"

    def mark_backend_disconnected(self, index: int, error: Exception | None = None) -> None:
        """Mark a backend as disconnected (e.g., from async processor connection failures).

        This allows external components (like AsyncOperationProcessor) to update
        the health state when they detect persistent connection issues.

        Args:
            index: The original backend index (not position in list).
            error: Optional exception that caused the disconnection.

        This is a silent update - it doesn't log transitions since the connection
        issues would have already been logged by the async processor.
        """
        if error is None:
            error = Exception("Connection lost")
        with self._lock:
            pos = self._find_state_position(index)
            if pos is None:
                return  # Backend not found (shouldn't happen)
            current = self._backend_states[pos]
            # Only update if currently healthy - don't override existing failure state
            if isinstance(current.health, Healthy):
                new_health = Degraded(consecutive_failures=FAILURE_THRESHOLD, last_error=error)
                self._backend_states[pos] = BackendState(
                    backend=current.backend,
                    index=current.index,
                    health=new_health,
                )

    # =========================================================================
    # NeptuneBackend Interface Implementation
    # =========================================================================

    def get_display_address(self) -> str:
        """Returns display address from the first backend."""
        return self._backend_states[0].backend.get_display_address()

    @property
    def _client_config(self):
        """Proxy to primary backend's client config for backward compatibility.

        This allows code that accesses backend._client_config to work with MultiBackend.
        """
        return self._backend_states[0].backend._client_config

    def get_project(self, project_id):
        """Get project from the first healthy backend."""
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.get_project(project_id)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
                logger.warning(f"{self._backend_id(state.index)} failed to get project: {e}")

        self._raise_all_failed(errors)

    def get_available_projects(self, workspace_id=None, search_term=None):
        """Get available projects from the first healthy backend."""
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.get_available_projects(workspace_id, search_term)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))

        self._raise_all_failed(errors)

    def get_available_workspaces(self):
        """Get available workspaces from the first healthy backend."""
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.get_available_workspaces()
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))

        self._raise_all_failed(errors)

    def create_run(
        self,
        project_id: UniqueId,
        git_info: GitInfo | None = None,
        custom_run_id: str | None = None,
        notebook_id: str | None = None,
        checkpoint_id: str | None = None,
        *,
        _external_id: str | None = None,
        _external_sys_id: str | None = None,
    ) -> ApiExperiment:
        """Create run on primary backend first, then fan out to remaining backends.

        The primary backend (index 0) is called first to generate the authoritative
        UUID and sys_id. These IDs are then passed to remaining backends so all
        backends share the same identifiers.

        Args:
            project_id: The project to create the run in
            git_info: Optional git repository information
            custom_run_id: Optional user-defined run ID for cross-backend resume
            notebook_id: Optional notebook ID
            checkpoint_id: Optional checkpoint ID
            _external_id: Internal use only - UUID from primary backend
            _external_sys_id: Internal use only - sys_id from primary backend

        Returns:
            ApiExperiment from the primary backend (index 0).

        Retry Policy:
            - Primary backend must succeed for run creation to proceed
            - Remaining backends are attempted in parallel
            - Failed backends are marked as degraded and will be retried periodically
            - Maximum total time for retries: 30 seconds
        """
        self._check_not_closed()

        errors: list[Exception] = []

        # Snapshot backends under lock
        with self._lock:
            backends_snapshot = list(self._backend_states)

        if not backends_snapshot:
            raise AllBackendsFailedError([])

        # Check shutdown before proceeding
        if self._shutdown_event.is_set():
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        # Step 1: Call primary backend (index 0) first to get authoritative IDs
        primary_state = backends_snapshot[0]
        primary_result: ApiExperiment | None = None
        total_backends = len(backends_snapshot)
        is_multi_backend = total_backends > 1

        if is_multi_backend:
            logger.info(f"Initializing run on {total_backends} backends...")
            logger.info(f"{self._backend_id(primary_state.index)}: initializing (primary)...")

        try:
            primary_result = primary_state.backend.create_run(
                project_id,
                git_info,
                custom_run_id,
                notebook_id,
                checkpoint_id,
                _external_id=_external_id,
                _external_sys_id=_external_sys_id,
            )
            self._transition_on_success(primary_state.index)
            if is_multi_backend:
                logger.info(f"{self._backend_id(primary_state.index)}: initialized (primary)")
        except Exception as e:
            self._transition_on_failure(primary_state.index, e)
            error_type = type(e).__name__
            if is_multi_backend:
                logger.warning(f"{self._backend_id(primary_state.index)}: failed (primary) - {error_type}: {e}")
            else:
                logger.warning(f"{self._backend_id(primary_state.index)} failed to create run: {error_type}: {e}")
            errors.append(BackendError(backend_index=primary_state.index, cause=e))
            self._raise_all_failed(errors)

        # Step 2: Fan out to remaining backends with primary's IDs
        remaining_backends = backends_snapshot[1:]
        if not remaining_backends:
            return primary_result

        def create_on_secondary(state: BackendState):
            logger.info(f"{self._backend_id(state.index)}: initializing (secondary)...")
            try:
                result = state.backend.create_run(
                    project_id,
                    git_info,
                    custom_run_id,
                    notebook_id,
                    checkpoint_id,
                    _external_id=primary_result.id,
                    _external_sys_id=primary_result.sys_id,
                )
                self._transition_on_success(state.index)
                logger.info(f"{self._backend_id(state.index)}: initialized (secondary)")
                return (state.index, result, None)
            except Exception as e:
                self._transition_on_failure(state.index, e)
                error_type = type(e).__name__
                return (state.index, None, f"{error_type}: {e}")

        # Execute remaining backends in parallel
        try:
            futures = {self._executor.submit(create_on_secondary, state): state for state in remaining_backends}
        except RuntimeError:
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        try:
            for future in as_completed(futures, timeout=MAX_RETRY_TIMEOUT_SECONDS):
                idx, result, error = future.result()
                if error:
                    logger.warning(f"{self._backend_id(idx)}: failed (secondary) - {error}")
                    errors.append(BackendError(backend_index=idx, cause=error))
        except FuturesTimeoutError:
            logger.warning(f"create_run() timed out after {MAX_RETRY_TIMEOUT_SECONDS}s")

        # Log initialization summary (only for multi-backend)
        successful_count = 1 + len(remaining_backends) - len(errors)  # 1 for primary
        if errors:
            logger.warning(f"Run initialization completed: {successful_count}/{total_backends} backends ready")
        else:
            logger.info(f"Run initialization completed: {successful_count}/{total_backends} backends ready")

        # Return primary backend's result (authoritative)
        return primary_result

    def create_model(self, project_id, key):
        """Create model on all backends in parallel."""
        self._check_not_closed()
        results: dict[int, ApiExperiment] = {}
        errors: list[Exception] = []

        with self._lock:
            backends_snapshot = list(self._backend_states)

        def create_on_backend(state: BackendState):
            try:
                result = state.backend.create_model(project_id, key)
                self._transition_on_success(state.index)
                return (state.index, result, None)
            except Exception as e:
                self._transition_on_failure(state.index, e)
                return (state.index, None, e)

        if self._shutdown_event.is_set():
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        try:
            futures = {self._executor.submit(create_on_backend, state): state for state in backends_snapshot}
        except RuntimeError:
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        try:
            for future in as_completed(futures, timeout=MAX_RETRY_TIMEOUT_SECONDS):
                idx, result, error = future.result()
                if error:
                    errors.append(BackendError(backend_index=idx, cause=error))
                else:
                    results[idx] = result
        except FuturesTimeoutError:
            pass

        if not results:
            self._raise_all_failed(errors)

        lowest_index = min(results.keys())
        return results[lowest_index]

    def create_model_version(self, project_id, model_id):
        """Create model version on all backends in parallel."""
        self._check_not_closed()
        results: dict[int, ApiExperiment] = {}
        errors: list[Exception] = []

        with self._lock:
            backends_snapshot = list(self._backend_states)

        def create_on_backend(state: BackendState):
            try:
                result = state.backend.create_model_version(project_id, model_id)
                self._transition_on_success(state.index)
                return (state.index, result, None)
            except Exception as e:
                self._transition_on_failure(state.index, e)
                return (state.index, None, e)

        if self._shutdown_event.is_set():
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        try:
            futures = {self._executor.submit(create_on_backend, state): state for state in backends_snapshot}
        except RuntimeError:
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        try:
            for future in as_completed(futures, timeout=MAX_RETRY_TIMEOUT_SECONDS):
                idx, result, error = future.result()
                if error:
                    errors.append(BackendError(backend_index=idx, cause=error))
                else:
                    results[idx] = result
        except FuturesTimeoutError:
            pass

        if not results:
            self._raise_all_failed(errors)

        lowest_index = min(results.keys())
        return results[lowest_index]

    def get_metadata_container(self, container_id, expected_container_type):
        """Get metadata container from first healthy backend."""
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.get_metadata_container(container_id, expected_container_type)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))

        self._raise_all_failed(errors)

    def create_checkpoint(self, notebook_id, jupyter_path):
        """Create checkpoint on first healthy backend."""
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.create_checkpoint(notebook_id, jupyter_path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))

        self._raise_all_failed(errors)

    def execute_operations(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        operations: list[Operation],
        operation_storage: OperationStorage,
    ) -> tuple[int, list[NeptuneException]]:
        """Fan out to all backends in parallel. Succeed if ANY backend succeeds.

        Args:
            container_id: The run/container identifier
            container_type: Type of container (Run, Model, etc.)
            operations: List of operations to execute
            operation_storage: Storage for operation data

        Returns:
            Tuple of (max_processed_count, backend_errors) where:
            - max_processed_count: Maximum operations processed by any successful backend
            - backend_errors: list[NeptuneException] from completely FAILED backends only.

        Error Handling:
            - If ALL backends fail: raises AllBackendsFailedError with all errors
            - If SOME backends fail: returns success with BackendError list from failed backends
        """
        self._check_not_closed()

        backend_errors: list[NeptuneException] = []
        results: list[tuple[int, list[NeptuneException]]] = []

        backends_to_use = self._get_routable_backends()

        logger.debug(f"Flushing {len(operations)} operations to {len(backends_to_use)} backend(s)")

        def execute_on_backend(state: BackendState):
            try:
                result = state.backend.execute_operations(container_id, container_type, operations, operation_storage)
                # Atomic transition to Healthy
                self._transition_on_success(state.index)
                return (state.index, result, None)
            except Exception as e:
                # Atomic transition based on failure (may become Degraded)
                self._transition_on_failure(state.index, e)
                return (state.index, None, e)

        # Check shutdown before submitting to avoid RuntimeError
        if self._shutdown_event.is_set():
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        # Execute in parallel
        try:
            futures = {self._executor.submit(execute_on_backend, state): state for state in backends_to_use}
        except RuntimeError:
            # Executor was shut down between our check and submit
            raise NeptuneMultiBackendClosedError("MultiBackend has been closed")

        for future in as_completed(futures):
            idx, result, error = future.result()
            if error:
                logger.warning(f"{self._backend_id(idx)} failed: {error}")
                backend_errors.append(BackendError(backend_index=idx, cause=error))
            else:
                results.append(result)

        if not results:
            self._raise_all_failed(backend_errors)

        # Return maximum processed count (optimistic - at least one backend processed this many)
        max_processed = max(r[0] for r in results)

        # Log partial errors from successful backends at DEBUG (not returned to caller)
        for processed, partial_errors in results:
            for err in partial_errors:
                logger.debug(f"Partial error from successful backend: {err}")

        logger.debug(f"Buffer flush complete: {max_processed} operations processed")

        # Return only errors from completely failed backends
        return max_processed, backend_errors

    def get_attributes(self, container_id: str, container_type: ContainerType) -> list[Attribute]:
        """Read operations: try healthy backends first, use first successful response."""
        self._check_not_closed()

        backends_to_try = self._get_routable_backends()
        errors = []

        for state in backends_to_try:
            try:
                result = state.backend.get_attributes(container_id, container_type)
                # Atomic transition to Healthy
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                # Atomic transition based on failure (may become Degraded)
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
                logger.warning(f"{self._backend_id(state.index)} failed to get attributes: {e}")

        self._raise_all_failed(errors)

    # Delegate read operations to first healthy backend
    def download_file(self, container_id, container_type, path, destination=None, progress_bar=None):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.download_file(
                    container_id=container_id,
                    container_type=container_type,
                    path=path,
                    destination=destination,
                    progress_bar=progress_bar,
                )
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def download_file_set(self, container_id, container_type, path, destination=None, progress_bar=None):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.download_file_set(
                    container_id=container_id,
                    container_type=container_type,
                    path=path,
                    destination=destination,
                    progress_bar=progress_bar,
                )
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_float_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_float_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_int_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_int_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_bool_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_bool_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_file_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_file_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_string_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_string_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_datetime_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_datetime_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_artifact_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_artifact_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def list_artifact_files(self, project_id, artifact_hash):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.list_artifact_files(project_id, artifact_hash)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_float_series_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_float_series_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_string_series_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_string_series_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_string_set_attribute(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_string_set_attribute(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def download_file_series_by_index(self, container_id, container_type, path, index, destination, progress_bar):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.download_file_series_by_index(
                    container_id, container_type, path, index, destination, progress_bar
                )
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_image_series_values(self, container_id, container_type, path, offset, limit):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_image_series_values(container_id, container_type, path, offset, limit)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_string_series_values(self, container_id, container_type, path, offset, limit):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_string_series_values(container_id, container_type, path, offset, limit)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_float_series_values(self, container_id, container_type, path, offset, limit):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.get_float_series_values(container_id, container_type, path, offset, limit)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def get_run_url(self, run_id, workspace, project_name, sys_id):
        return self._backend_states[0].backend.get_run_url(run_id, workspace, project_name, sys_id)

    def get_all_run_urls(self, run_id, workspace, project_name, sys_id) -> list[str]:
        """Get run URLs from all backends."""
        urls = []
        for state in self._backend_states:
            try:
                url = state.backend.get_run_url(run_id, workspace, project_name, sys_id)
                urls.append(url)
            except Exception:
                pass  # Skip backends that fail to generate URL
        return urls

    def get_project_url(self, project_id, workspace, project_name):
        return self._backend_states[0].backend.get_project_url(project_id, workspace, project_name)

    def get_model_url(self, model_id, workspace, project_name, sys_id):
        return self._backend_states[0].backend.get_model_url(model_id, workspace, project_name, sys_id)

    def get_model_version_url(self, model_version_id, model_id, workspace, project_name, sys_id):
        return self._backend_states[0].backend.get_model_version_url(
            model_version_id, model_id, workspace, project_name, sys_id
        )

    def fetch_atom_attribute_values(self, container_id, container_type, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.fetch_atom_attribute_values(container_id, container_type, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def search_leaderboard_entries(
        self,
        project_id,
        types=None,
        query=None,
        columns=None,
        limit=None,
        sort_by="sys/creation_time",
        ascending=False,
        progress_bar=None,
    ):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.search_leaderboard_entries(
                    project_id=project_id,
                    types=types,
                    query=query,
                    columns=columns,
                    limit=limit,
                    sort_by=sort_by,
                    ascending=ascending,
                    progress_bar=progress_bar,
                )
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def list_fileset_files(self, attribute, container_id, path):
        self._check_not_closed()
        backends_to_try = self._get_routable_backends()
        errors = []
        for state in backends_to_try:
            try:
                result = state.backend.list_fileset_files(attribute, container_id, path)
                self._transition_on_success(state.index)
                return result
            except Exception as e:
                self._transition_on_failure(state.index, e)
                errors.append(BackendError(backend_index=state.index, cause=e))
        self._raise_all_failed(errors)

    def close(self) -> None:
        """Close all backends and cleanup resources.

        Thread Safety:
            1. Sets shutdown event to reject new operations
            2. Cancels health check timer
            3. Shuts down executor (waits for in-flight operations to complete)
            4. Closes all backends sequentially (they're now idle)

        This ordering ensures backends are not closed while operations are in-flight.
        """
        # Signal shutdown to prevent new operations and timer rescheduling
        self._shutdown_event.set()

        # Stop health check timer
        if self._health_check_timer:
            self._health_check_timer.cancel()

        # Shutdown executor and wait for in-flight operations to complete
        # This must happen BEFORE closing backends to avoid closing while in use
        self._executor.shutdown(wait=True)

        # Now close all backends (they're idle, no concurrent operations)
        # Sequential is fine here since backends are idle
        is_multi_backend = len(self._backend_states) > 1
        if is_multi_backend:
            logger.info("Closing connection to backends...")

        for state in self._backend_states:
            health_status = self._format_health_status(state.health)
            if is_multi_backend:
                logger.info(f"{self._backend_id(state.index)}: closing ({health_status})...")
            try:
                state.backend.close()
                if is_multi_backend:
                    logger.info(f"{self._backend_id(state.index)}: closed")
            except Exception as e:
                error_type = type(e).__name__
                if is_multi_backend:
                    logger.warning(f"{self._backend_id(state.index)}: failed to close - {error_type}: {e}")
                else:
                    logger.warning(f"Error closing backend {state.index}: {error_type}: {e}")
