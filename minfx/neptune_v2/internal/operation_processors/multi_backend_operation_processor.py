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
"""Multi-backend operation processor for parallel async processing to multiple backends.

Each backend gets its own AsyncOperationProcessor with separate:
- data_path / upload_path (no file conflicts)
- DiskQueue (independent retry/recovery)
- ConsumerThread (parallel processing)
"""

from __future__ import annotations

__all__ = ("MultiBackendOperationProcessor",)

import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as futures_wait
from pathlib import Path
from typing import TYPE_CHECKING

from minfx.neptune_v2.constants import ASYNC_DIRECTORY
from minfx.neptune_v2.internal.operation import Operation
from minfx.neptune_v2.internal.operation import UploadFile
from minfx.neptune_v2.internal.operation_processors.async_operation_processor import AsyncOperationProcessor
from minfx.neptune_v2.internal.operation_processors.operation_processor import OperationProcessor
from minfx.neptune_v2.internal.operation_processors.utils import get_container_full_path
from minfx.neptune_v2.internal.utils.backend_name import backend_name_from_url
from minfx.neptune_v2.internal.utils.logger import get_logger

logger = get_logger()

if TYPE_CHECKING:
    from queue import Queue

    from minfx.neptune_v2.core.components.operation_storage import OperationStorage
    from minfx.neptune_v2.internal.backends.multi_backend import MultiBackend
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import UniqueId
    from minfx.neptune_v2.internal.signals_processing.signals import Signal


class MultiBackendOperationProcessor(OperationProcessor):
    """Operation processor that maintains separate async queues for each backend.

    This ensures file upload operations work correctly in multi-backend mode by
    giving each backend its own upload_path, preventing race conditions on file cleanup.
    """

    def __init__(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        multi_backend: MultiBackend,
        lock: threading.RLock,
        queue: Queue[Signal],
        sleep_time: float = 3,
        batch_size: int = 2048,
    ):
        self._container_id = container_id
        self._container_type = container_type
        self._lock = lock
        self._multi_backend = multi_backend  # Keep reference for health updates

        # Extract backend states (preserves original indices)
        backend_states = multi_backend._backend_states

        # Store backend indices and addresses for logging (using original indices)
        self._backend_indices: list[int] = [state.index for state in backend_states]
        self._backend_addresses: dict[int, str] = {
            state.index: state.backend.get_display_address() for state in backend_states
        }

        # Create base path ONCE (it contains a random key)
        base_path = get_container_full_path(ASYNC_DIRECTORY, container_id, container_type)

        # Log backend index → address mapping at startup
        if len(backend_states) > 1:
            logger.info("Multi-backend configuration:")
            for state in backend_states:
                logger.info(f"  [backend {state.index}] {state.backend.get_display_address()}")

        # Create separate AsyncOperationProcessor for each backend
        self._processors: list[AsyncOperationProcessor] = []
        for state in backend_states:
            original_index = state.index
            backend_url = state.backend.get_display_address()
            # Each backend gets its own data_path using DNS-based name
            backend_name = backend_name_from_url(backend_url)
            backend_path = base_path / backend_name

            processor = AsyncOperationProcessor(
                container_id=container_id,
                container_type=container_type,
                backend=state.backend,
                lock=threading.RLock(),  # Each processor needs its own lock
                queue=queue,  # Shared signal queue
                sleep_time=sleep_time,
                batch_size=batch_size,
                data_path=backend_path,
                should_print_logs=True,  # All backends log their sync status
                backend_index=original_index,  # Use original index for logging
                backend_address=backend_url,  # Store backend address in metadata
            )
            self._processors.append(processor)

        # Use primary processor's operation_storage for initial file creation
        self._primary_processor = self._processors[0]

    @property
    def _consumer(self):
        """Provide access to the primary processor's consumer for backward compatibility.

        This is used by CLI tests that access container._op_processor._consumer.
        """
        return self._primary_processor._consumer

    def _backend_id(self, processor_position: int) -> str:
        """Format backend identifier for logging."""
        original_index = self._backend_indices[processor_position]
        return f"[backend {original_index}] ({self._backend_addresses[original_index]})"

    @property
    def operation_storage(self) -> OperationStorage:
        """Return primary processor's storage for initial file writes."""
        return self._primary_processor.operation_storage

    @property
    def data_path(self) -> Path:
        """Return primary processor's data path for compatibility with tests."""
        return self._primary_processor.data_path

    def enqueue_operation(self, op: Operation, *, wait: bool) -> None:
        """Enqueue operation to all backend processors.

        For file upload operations, copies the file to each processor's upload_path
        before enqueuing.
        """
        # For UploadFile with tmp_file_name, copy file to each processor's upload_path
        if isinstance(op, UploadFile) and op.tmp_file_name:
            self._replicate_upload_file(op)

        # Enqueue to all processors
        for processor in self._processors:
            processor.enqueue_operation(op, wait=wait)

    def _replicate_upload_file(self, op: UploadFile) -> None:
        """Copy uploaded file from primary to all secondary processors."""
        primary_storage = self._primary_processor.operation_storage
        source_path = Path(primary_storage.upload_path) / op.tmp_file_name

        if not source_path.exists():
            return  # File might be from file_path, not tmp_file_name

        # Copy to each secondary processor's upload_path
        for processor in self._processors[1:]:
            dest_path = Path(processor.operation_storage.upload_path) / op.tmp_file_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

    def start(self) -> None:
        """Start all processors."""
        for processor in self._processors:
            processor.start()

    def pause(self) -> None:
        """Pause all processors."""
        for processor in self._processors:
            processor.pause()

    def resume(self) -> None:
        """Resume all processors."""
        for processor in self._processors:
            processor.resume()

    def flush(self) -> None:
        """Flush all processors."""
        if len(self._processors) > 1:
            logger.debug(f"Flushing buffers for {len(self._processors)} backend processors")
        for processor in self._processors:
            processor.flush()

    def wait(self) -> None:
        """Wait for all processors to complete pending operations in parallel."""
        if len(self._processors) == 1:
            self._processors[0].wait()
            return

        try:
            with ThreadPoolExecutor(max_workers=len(self._processors)) as executor:
                futures = [executor.submit(p.wait) for p in self._processors]
                futures_wait(futures)
        except RuntimeError as e:
            if "interpreter shutdown" not in str(e):
                raise
            # Interpreter shutting down - fall back to sequential
            for p in self._processors:
                p.wait()

    def stop(self, seconds: float | None = None) -> None:
        """Stop all processors in parallel with shared timeout."""
        if len(self._processors) == 1:
            self._processors[0].stop(seconds)
            self._update_multi_backend_health()
            return

        logger.info(f"Synchronizing {len(self._processors)} backends...")

        try:
            with ThreadPoolExecutor(max_workers=len(self._processors)) as executor:
                futures = [executor.submit(p.stop, seconds) for p in self._processors]
                futures_wait(futures)
        except RuntimeError as e:
            if "interpreter shutdown" not in str(e):
                raise
            # Interpreter shutting down - fall back to sequential
            for p in self._processors:
                p.stop(seconds)

        # Update multi-backend health state based on processor connection status
        self._update_multi_backend_health()

    def _update_multi_backend_health(self) -> None:
        """Update MultiBackend health state based on processor connection status.

        If a processor had connection issues (last_backoff_time > 0), mark the
        corresponding backend as disconnected so the health state is accurate.
        """
        for i, processor in enumerate(self._processors):
            # Check if the processor's consumer had connection issues
            if hasattr(processor, "_consumer") and processor._consumer.last_backoff_time > 0:
                # Use original index from _backend_indices
                original_index = self._backend_indices[i]
                self._multi_backend.mark_backend_disconnected(
                    original_index, Exception("Connection issues during sync")
                )

    def close(self) -> None:
        """Close all processors."""
        for processor in self._processors:
            processor.close()
