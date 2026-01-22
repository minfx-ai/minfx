#
# Copyright (c) 2022, Neptune Labs Sp. z o.o.
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
from __future__ import annotations

__all__ = ["get_backend"]

from typing import TYPE_CHECKING

from minfx.neptune_v2.exceptions import AllBackendsFailedError, BackendError
from minfx.neptune_v2.internal.backends.backend_config import (
    BackendConfig,
    configs_from_tokens,
)
from minfx.neptune_v2.internal.credentials import Credentials
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.types.mode import Mode

from .hosted_neptune_backend import HostedNeptuneBackend
from .multi_backend import MultiBackend
from .neptune_backend_mock import NeptuneBackendMock
from .offline_neptune_backend import OfflineNeptuneBackend

if TYPE_CHECKING:
    from .neptune_backend import NeptuneBackend

logger = get_logger()


def get_backend(
    mode: Mode,
    backends: list[BackendConfig] | None = None,
    proxies: dict | None = None,
) -> NeptuneBackend:
    """Create backend(s) from configuration.

    Always returns a MultiBackend, even for single-backend configurations.
    This simplifies the codebase by having a uniform backend type.

    Args:
        mode: Connection mode (async, sync, debug, offline, read-only).
        backends: List of BackendConfig objects specifying backend connections.
            If None, creates backends from NEPTUNE_API_TOKEN environment variable.
            For debug/offline modes, a dummy backend is created if no token is available.
        proxies: Default proxy configuration (used if config doesn't specify proxies).

    Returns:
        NeptuneBackend: Always returns a MultiBackend wrapping the configured backends.
    """
    # Debug and offline modes don't need real backends
    if mode == Mode.DEBUG:
        return NeptuneBackendMock()
    if mode == Mode.OFFLINE:
        return OfflineNeptuneBackend()

    # If backends not provided, create from NEPTUNE_API_TOKEN env var
    if backends is None:
        backends = configs_from_tokens(None, proxies=proxies)

    return _get_backend_from_configs(mode=mode, configs=backends, proxies=proxies)


def _get_backend_from_configs(
    mode: Mode,
    configs: list[BackendConfig],
    proxies: dict | None = None,
) -> NeptuneBackend:
    """Create backend(s) from a list of BackendConfig objects.

    Always returns a MultiBackend, even for single-backend configurations.

    Handles backend creation failures gracefully:
    - For single backend: exception propagates normally.
    - For multiple backends: logs a warning and continues if some fail.
    - Only raises AllBackendsFailedError if ALL backends fail to create.

    Args:
        mode: Connection mode.
        configs: List of BackendConfig objects.
        proxies: Default proxy configuration (used if config doesn't specify proxies).

    Returns:
        NeptuneBackend: Always returns a MultiBackend wrapping the configured backends.

    Raises:
        ValueError: If no backend configurations provided.
        AllBackendsFailedError: If all backends fail to create.
    """
    if not configs:
        raise ValueError("At least one backend configuration is required")

    total_backends = len(configs)
    is_multi = total_backends > 1

    if is_multi:
        logger.info(f"Connecting to {total_backends} backends...")

    backends: list[tuple[int, NeptuneBackend]] = []  # (original_index, backend) pairs
    creation_errors: list[BackendError] = []

    for index, config in enumerate(configs):
        effective_proxies = config.proxies or proxies
        role_marker = "(primary)" if index == 0 else "(secondary)"

        # Extract URL from token for logging before connection attempt
        backend_url = _get_url_from_token(config.api_token)

        if is_multi:
            logger.info(f"[backend {index}] ({backend_url}): connecting {role_marker}...")

        try:
            backend = _create_single_backend(
                mode=mode,
                api_token=config.api_token,
                proxies=effective_proxies,
                project_name_override=config.project,
                backend_index=index,  # Always pass index for queue size tracking
            )
            backends.append((index, backend))  # Preserve original index
            if is_multi:
                logger.info(f"[backend {index}] ({backend.get_display_address()}): connected {role_marker}")
        except Exception as e:
            if is_multi:
                # Multi-backend: log warning and continue
                error_type = type(e).__name__
                logger.warning(
                    f"[backend {index}] ({backend_url}): failed to connect {role_marker} - {error_type}: {e}"
                )
                creation_errors.append(BackendError(backend_index=index, cause=e))
            else:
                # Single backend: propagate exception
                raise

    if not backends:
        raise AllBackendsFailedError(creation_errors)

    if is_multi:
        if creation_errors:
            logger.warning(f"Backend connection completed: {len(backends)}/{total_backends} backends ready")
        else:
            logger.info(f"Backend connection completed: {len(backends)}/{total_backends} backends ready")

    # Always return MultiBackend (even for single backend)
    return MultiBackend.from_indexed_backends(backends)


def _get_url_from_token(api_token: str | None) -> str:
    """Extract the API URL from an API token for logging purposes."""
    if api_token is None:
        return "unknown"
    try:
        creds = Credentials.from_token(api_token)
        return creds.token_origin_address
    except Exception:
        return "unknown"


def _create_single_backend(
    mode: Mode,
    api_token: str | None = None,
    proxies: dict | None = None,
    project_name_override: str | None = None,
    backend_index: int | None = None,
) -> NeptuneBackend:
    """Create a single backend instance based on mode.

    Args:
        mode: Connection mode.
        api_token: API token for authentication.
        proxies: Proxy configuration.
        project_name_override: Optional project name to use instead of the main project.
            If specified, this backend will use this project for all operations.
        backend_index: Index of this backend for logging purposes (in multi-backend setups).
    """
    if mode in (Mode.ASYNC, Mode.SYNC, Mode.READ_ONLY):
        return HostedNeptuneBackend(
            credentials=Credentials.from_token(api_token=api_token),
            proxies=proxies,
            project_name_override=project_name_override,
            backend_index=backend_index,
        )
    if mode == Mode.DEBUG:
        return NeptuneBackendMock()
    if mode == Mode.OFFLINE:
        return OfflineNeptuneBackend()
    raise ValueError(f"mode should be one of {list(Mode)}")
