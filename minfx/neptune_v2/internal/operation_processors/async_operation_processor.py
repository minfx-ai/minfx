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

__all__ = ("AsyncOperationProcessor",)

import contextlib
import os
import threading
from pathlib import Path
from time import (
    monotonic,
    time,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from minfx.neptune_v2.common.backends.utils import (
    register_queue_size_provider,
    unregister_queue_size_provider,
)
from minfx.neptune_v2.common.warnings import (
    NeptuneWarning,
    warn_once,
)
from minfx.neptune_v2.constants import ASYNC_DIRECTORY
from minfx.neptune_v2.core.components.abstract import WithResources
from minfx.neptune_v2.core.components.metadata_file import MetadataFile
from minfx.neptune_v2.core.components.operation_storage import OperationStorage
from minfx.neptune_v2.core.components.queue.disk_queue import (
    DiskQueue,
    InMemoryQueue,
)
from minfx.neptune_v2.envs import (
    NEPTUNE_IN_MEMORY_QUEUE,
    NEPTUNE_SYNC_AFTER_STOP_TIMEOUT,
)
from minfx.neptune_v2.exceptions import NeptuneSynchronizationAlreadyStoppedException
from minfx.neptune_v2.internal.init.parameters import DEFAULT_STOP_TIMEOUT
from minfx.neptune_v2.internal.operation import Operation
from minfx.neptune_v2.internal.operation_processors.operation_logger import ProcessorStopLogger
from minfx.neptune_v2.internal.operation_processors.operation_processor import OperationProcessor
from minfx.neptune_v2.internal.operation_processors.utils import (
    common_metadata,
    get_container_full_path,
)
from minfx.neptune_v2.internal.signals_processing.utils import (
    signal_batch_lag,
    signal_batch_processed,
    signal_batch_started,
)
from minfx.neptune_v2.internal.state import OperationAcceptance
from minfx.neptune_v2.internal.threading.daemon import Daemon
from minfx.neptune_v2.internal.utils.disk_utilization import ensure_disk_not_overutilize
from minfx.neptune_v2.internal.utils.logger import get_logger

if TYPE_CHECKING:
    from queue import Queue

    from minfx.neptune_v2.common.exceptions import NeptuneException
    from minfx.neptune_v2.core.components.abstract import Resource
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import UniqueId
    from minfx.neptune_v2.internal.operation_processors.operation_logger import ProcessorStopSignal
    from minfx.neptune_v2.internal.signals_processing.signals import Signal

logger = get_logger()


def serializer(op: Operation) -> dict[str, Any]:
    return op.to_dict()


class AsyncOperationProcessor(WithResources, OperationProcessor):
    STOP_QUEUE_STATUS_UPDATE_FREQ_SECONDS = 10.0
    STOP_QUEUE_MAX_TIME_NO_CONNECTION_SECONDS = float(os.getenv(NEPTUNE_SYNC_AFTER_STOP_TIMEOUT, DEFAULT_STOP_TIMEOUT))

    def __init__(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        backend: NeptuneBackend,
        lock: threading.RLock,
        queue: Queue[Signal],
        sleep_time: float = 3,
        batch_size: int = 2048,
        data_path: Path | None = None,
        should_print_logs: bool = True,
        backend_index: int | None = None,
        backend_address: str | None = None,
    ):
        self._should_print_logs: bool = should_print_logs
        self._backend_index: int | None = backend_index

        self._data_path = (
            data_path if data_path else get_container_full_path(ASYNC_DIRECTORY, container_id, container_type)
        )

        # Initialize directory
        self._data_path.mkdir(parents=True, exist_ok=True)

        # Build metadata with optional backend address
        metadata = common_metadata(mode="async", container_id=container_id, container_type=container_type)
        if backend_address:
            metadata["backendAddress"] = backend_address

        self._metadata_file = MetadataFile(
            data_path=self._data_path,
            metadata=metadata,
        )
        self._operation_storage = OperationStorage(data_path=self._data_path)

        # Use in-memory queue for benchmarking if NEPTUNE_IN_MEMORY_QUEUE is set
        if os.environ.get(NEPTUNE_IN_MEMORY_QUEUE):
            logger.info("Using in-memory queue (NEPTUNE_IN_MEMORY_QUEUE is set)")
            self._queue = InMemoryQueue(lock=lock)
        else:
            self._queue = DiskQueue(
                data_path=self._data_path,
                to_dict=serializer,
                from_dict=Operation.from_dict,
                lock=lock,
            )

        self._container_id: UniqueId = container_id
        self._container_type: ContainerType = container_type
        self._backend: NeptuneBackend = backend
        self._batch_size: int = batch_size
        self._last_version: int = 0
        self._consumed_version: int = 0
        self._consumer: Daemon = self.ConsumerThread(self, sleep_time, batch_size)
        self._lock: threading.RLock = lock
        self._signals_queue: Queue[Signal] = queue
        self._operation_acceptance: OperationAcceptance = OperationAcceptance.ACCEPTING

        # Caller is responsible for taking this lock
        self._waiting_cond = threading.Condition(lock=lock)

        # Queue backpressure tracking: threshold = queue_size // 1000
        # Used to log warnings when queue grows and info when backpressure lifts
        self._queue_threshold: int = 0

    @property
    def operation_storage(self) -> OperationStorage:
        return self._operation_storage

    @property
    def data_path(self) -> Path:
        return self._data_path

    @property
    def resources(self) -> tuple[Resource, ...]:
        return self._metadata_file, self._operation_storage, self._queue

    @ensure_disk_not_overutilize
    def enqueue_operation(self, op: Operation, *, wait: bool) -> None:
        if not self._operation_acceptance.is_accepting():
            warn_once("Not accepting operations", exception=NeptuneWarning)
            return

        self._last_version = self._queue.put(op)
        self._check_queue_backpressure()

        if self._check_queue_size():
            self._consumer.wake_up()
        if wait:
            self.wait()

    def start(self) -> None:
        # Register queue size provider for retry logging
        register_queue_size_provider(self._backend_index, self._queue.size)
        self._consumer.start()

    def pause(self) -> None:
        self._consumer.pause()
        self.flush()

    def resume(self) -> None:
        self._consumer.resume()

    def wait(self) -> None:
        self.flush()
        waiting_for_version = self._last_version
        self._consumer.wake_up()

        # Probably reentering lock just for sure
        with self._waiting_cond:
            self._waiting_cond.wait_for(
                lambda: self._consumed_version >= waiting_for_version or not self._consumer.is_running()
            )
        if not self._consumer.is_running():
            raise NeptuneSynchronizationAlreadyStoppedException

    def _check_queue_size(self) -> bool:
        return self._queue.size() > self._batch_size / 2

    # Queue backpressure threshold step (warn every N ops)
    QUEUE_BACKPRESSURE_THRESHOLD = 5000

    def _check_queue_backpressure(self) -> None:
        """Check if queue size crossed a new threshold and log warning."""
        size = self._queue.size()
        current_threshold = size // self.QUEUE_BACKPRESSURE_THRESHOLD

        if current_threshold > self._queue_threshold:
            # Log warning for new threshold(s) crossed
            backend_prefix = f"[backend {self._backend_index}] " if self._backend_index is not None else ""
            ops_queued = current_threshold * self.QUEUE_BACKPRESSURE_THRESHOLD
            logger.warning(
                "%sQueue backpressure: %d ops queued (sync may be slower than logging)",
                backend_prefix,
                ops_queued,
            )
            self._queue_threshold = current_threshold

    def _check_queue_backpressure_lifted(self) -> None:
        """Check if backpressure lifted (queue dropped below threshold) and log info."""
        if self._queue_threshold == 0:
            return  # No backpressure was active

        size = self._queue.size()
        if size < self.QUEUE_BACKPRESSURE_THRESHOLD:
            backend_prefix = f"[backend {self._backend_index}] " if self._backend_index is not None else ""
            logger.info(
                "%sQueue backpressure lifted (%d ops remaining)",
                backend_prefix,
                size,
            )
            self._queue_threshold = 0

    def _wait_for_queue_empty(
        self,
        initial_queue_size: int,
        seconds: float | None,
        signal_queue: Queue[ProcessorStopSignal] | None = None,
    ) -> None:
        waiting_start: float = monotonic()
        time_elapsed: float = 0.0
        max_reconnect_wait_time: float = self.STOP_QUEUE_MAX_TIME_NO_CONNECTION_SECONDS if seconds is None else seconds
        op_logger = ProcessorStopLogger(
            processor_id=id(self),
            signal_queue=signal_queue,
            logger=logger,
            should_print_logs=self._should_print_logs,
            backend_index=self._backend_index,
            data_path=str(self._data_path),
            total_ops=self._last_version,
        )
        if initial_queue_size > 0:
            if self._consumer.last_backoff_time > 0:
                op_logger.log_connection_interruption(max_reconnect_wait_time)
            else:
                op_logger.log_remaining_operations(size_remaining=initial_queue_size)

        while True:
            if seconds is None:
                if self._consumer.last_backoff_time == 0:
                    # reset `waiting_start` on successful action
                    waiting_start = monotonic()
                # Always cap by max_reconnect_wait_time - even if not yet disconnected,
                # disconnection could happen during the wait. Cap ensures we check promptly.
                remaining = max(max_reconnect_wait_time - time_elapsed, 0.0)
                wait_time = min(remaining, self.STOP_QUEUE_STATUS_UPDATE_FREQ_SECONDS)
            else:
                wait_time = max(
                    min(
                        seconds - time_elapsed,
                        self.STOP_QUEUE_STATUS_UPDATE_FREQ_SECONDS,
                    ),
                    0.0,
                )
            self._queue.wait_for_empty(wait_time)
            size_remaining = self._queue.size()
            already_synced = initial_queue_size - size_remaining
            already_synced_proc = (already_synced / initial_queue_size) * 100 if initial_queue_size else 100
            if size_remaining == 0:
                op_logger.log_success(ops_synced=initial_queue_size)
                return

            time_elapsed = monotonic() - waiting_start
            if self._consumer.last_backoff_time > 0 and time_elapsed >= max_reconnect_wait_time:
                op_logger.log_reconnect_failure(
                    max_reconnect_wait_time=max_reconnect_wait_time,
                    size_remaining=size_remaining,
                )
                return

            if seconds is not None and wait_time == 0:
                op_logger.log_sync_failure(seconds=seconds, size_remaining=size_remaining)
                return

            if not self._consumer.is_running():
                exception = NeptuneSynchronizationAlreadyStoppedException()
                logger.warning(str(exception))
                return

            op_logger.log_still_waiting(
                size_remaining=size_remaining,
                already_synced=already_synced,
                already_synced_proc=already_synced_proc,
                is_disconnected=self._consumer.last_backoff_time > 0,
            )

    def stop(self, seconds: float | None = None, signal_queue: Queue[ProcessorStopSignal] | None = None) -> None:
        ts = time()
        self.flush()
        if self._consumer.is_running():
            self._consumer.disable_sleep()
            self._consumer.wake_up()
            self._wait_for_queue_empty(
                initial_queue_size=self._queue.size(),
                seconds=seconds,
                signal_queue=signal_queue,
            )
            self._consumer.interrupt()
        sec_left = None if seconds is None else seconds - (time() - ts)
        self._consumer.join(sec_left)

        # Close resources
        self.close()

        # Remove local files
        if self._queue.is_empty():
            self.cleanup()

    def cleanup(self) -> None:
        super().cleanup()
        with contextlib.suppress(OSError):
            self._data_path.rmdir()

    def close(self) -> None:
        self._operation_acceptance = OperationAcceptance.REJECTING
        # Unregister queue size provider
        unregister_queue_size_provider(self._backend_index)
        super().close()

    class ConsumerThread(Daemon):
        def __init__(
            self,
            processor: AsyncOperationProcessor,
            sleep_time: float,
            batch_size: int,
        ):
            super().__init__(sleep_time=sleep_time, name="NeptuneAsyncOpProcessor")
            self._processor: AsyncOperationProcessor = processor
            self._batch_size: int = batch_size
            self._last_flush: float = 0.0

        def run(self) -> None:
            try:
                super().run()
            except Exception:
                with self._processor._waiting_cond:
                    self._processor._waiting_cond.notify_all()
                raise

        def work(self) -> None:
            ts = time()
            if ts - self._last_flush >= self._sleep_time:
                self._last_flush = ts
                self._processor._queue.flush()
                logger.debug("Disk queue flushed to persistent storage")

            while True:
                batch = self._processor._queue.get_batch(self._batch_size)
                if not batch:
                    return

                signal_batch_started(queue=self._processor._signals_queue)
                self.process_batch([element.obj for element in batch], batch[-1].ver, batch[-1].at)

        # WARNING: Be careful when changing this function. It is used in the experimental package
        def _handle_errors(self, errors: list[NeptuneException]) -> None:
            for error in errors:
                # Skip known benign errors from Neptune backend
                error_str = str(error)
                if "sys/state is read only" in error_str:
                    # Neptune.ai doesn't allow setting sys/state on runs - this is expected
                    logger.debug("Skipped setting sys/state (read-only on Neptune backend)")
                    continue

                logger.error(
                    "Error occurred during asynchronous operation processing: %s",
                    error,
                )

        @Daemon.ConnectionRetryWrapper(
            kill_message=("Killing Minfx asynchronous thread. Unsynchronized data is saved on disk.")
        )
        def process_batch(self, batch: list[Operation], version: int, occurred_at: float | None = None) -> None:
            if occurred_at is not None:
                signal_batch_lag(queue=self._processor._signals_queue, lag=time() - occurred_at)

            expected_count = len(batch)
            version_to_ack = version - expected_count
            while True:
                # TODO: Handle Metadata errors
                processed_count, errors = self._processor._backend.execute_operations(
                    container_id=self._processor._container_id,
                    container_type=self._processor._container_type,
                    operations=batch,
                    operation_storage=self._processor._operation_storage,
                )

                signal_batch_processed(queue=self._processor._signals_queue)
                version_to_ack += processed_count
                batch = batch[processed_count:]

                with self._processor._waiting_cond:
                    self._processor._queue.ack(version_to_ack)
                    self._processor._check_queue_backpressure_lifted()

                    self._handle_errors(errors)

                    self._processor._consumed_version = version_to_ack

                    if version_to_ack == version:
                        self._processor._waiting_cond.notify_all()
                        return
