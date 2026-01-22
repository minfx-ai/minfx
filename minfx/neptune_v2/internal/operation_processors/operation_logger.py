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
__all__ = [
    "ProcessorStopLogger",
    "ProcessorStopSignal",
    # Discriminated union signal types (Rust-style tagged unions)
    "ConnectionInterruptedSignal",
    "WaitingForOperationsSignal",
    "SuccessSignal",
    "SyncFailureSignal",
    "ReconnectFailureSignal",
    "StillWaitingSignal",
]

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from queue import Queue

CONNECTION_INTERRUPTED_MSG = (
    "We have been experiencing connection interruptions during your run."
    " Minfx client will now try to resume connection and sync data for the next"
    " %s seconds."
    " You can also kill this process - data will be saved for manual sync."
)

# Messages with backend index for multi-backend
WAITING_FOR_OPERATIONS_MSG = "Waiting for the remaining %s operations to synchronize. Do not kill this process."
WAITING_FOR_OPERATIONS_WITH_BACKEND_MSG = (
    "[backend %s] Waiting for the remaining %s operations to synchronize. Do not kill this process."
)

SUCCESS_MSG = "All %s operations synced (out of %s total over the course of the run), thanks for waiting!"
SUCCESS_WITH_BACKEND_MSG = "[backend %s] All %s operations synced (out of %s total), thanks for waiting!"

SYNC_FAILURE_MSG = (
    "Failed to sync all operations in %s seconds."
    " You have %s unsynchronized operations saved. Run\n  minfx sync\nto upload manually. Data path: %s"
)

RECONNECT_FAILURE_MSG = (
    "Failed to reconnect in %s seconds."
    " You have %s unsynchronized operations saved. Run\n  minfx sync\nto upload manually. Data path: %s"
)
RECONNECT_FAILURE_WITH_BACKEND_MSG = (
    "[backend %s] Failed to reconnect in %s seconds."
    " You have %s unsynchronized operations saved. Run\n  minfx sync\nto upload manually. Data path: %s"
)

SYNC_FAILURE_WITH_BACKEND_MSG = (
    "[backend %s] Failed to sync all operations in %s seconds."
    " You have %s unsynchronized operations saved. Run\n  minfx sync\nto upload manually. Data path: %s"
)

STILL_WAITING_MSG = "Still waiting for the remaining %s operations (%.2f%% done). Please wait."
STILL_WAITING_WITH_BACKEND_MSG = (
    "[backend %s] Still waiting for the remaining %s operations (%.2f%% done). Please wait."
)
STILL_WAITING_DISCONNECTED_MSG = (
    "Still waiting for the remaining %s operations (%.2f%% done). Connection interrupted, retrying..."
)
STILL_WAITING_DISCONNECTED_WITH_BACKEND_MSG = (
    "[backend %s] Still waiting for the remaining %s operations (%.2f%% done). Connection interrupted, retrying..."
)


# Discriminated union signal types (Rust-style tagged unions)
# Each signal type carries only the data it needs, making the API more explicit.


@dataclass(frozen=True)
class ConnectionInterruptedSignal:
    """Signal indicating connection interruption during sync."""

    processor_id: int
    max_reconnect_wait_time: float


@dataclass(frozen=True)
class WaitingForOperationsSignal:
    """Signal indicating waiting for operations to sync."""

    processor_id: int
    size_remaining: int


@dataclass(frozen=True)
class SuccessSignal:
    """Signal indicating successful sync completion."""

    processor_id: int
    ops_synced: int
    total_ops: int


@dataclass(frozen=True)
class SyncFailureSignal:
    """Signal indicating sync failure due to timeout."""

    processor_id: int
    seconds: float
    size_remaining: int


@dataclass(frozen=True)
class ReconnectFailureSignal:
    """Signal indicating reconnection failure."""

    processor_id: int
    max_reconnect_wait_time: float
    size_remaining: int


@dataclass(frozen=True)
class StillWaitingSignal:
    """Signal indicating sync is still in progress."""

    processor_id: int
    size_remaining: int
    already_synced: int
    already_synced_proc: float


# Union type for all processor stop signals (Rust-style enum with data)
ProcessorStopSignal = Union[
    ConnectionInterruptedSignal,
    WaitingForOperationsSignal,
    SuccessSignal,
    SyncFailureSignal,
    ReconnectFailureSignal,
    StillWaitingSignal,
]


class ProcessorStopLogger:
    def __init__(
        self,
        processor_id: int,
        signal_queue: Optional["Queue[ProcessorStopSignal]"],
        logger: logging.Logger,
        should_print_logs: bool = True,
        backend_index: Optional[int] = None,
        data_path: Optional[str] = None,
        total_ops: int = 0,
    ) -> None:
        self._id = processor_id
        self._signal_queue = signal_queue
        self._logger = logger
        self._should_print_logs = should_print_logs
        self._backend_index = backend_index
        self._data_path = data_path or "unknown"
        self._total_ops = total_ops

    def log_connection_interruption(self, max_reconnect_wait_time: float) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                ConnectionInterruptedSignal(
                    processor_id=self._id,
                    max_reconnect_wait_time=max_reconnect_wait_time,
                )
            )
        else:
            self._logger.warning(
                CONNECTION_INTERRUPTED_MSG,
                max_reconnect_wait_time,
                self._data_path,
            )

    def log_remaining_operations(self, size_remaining: int) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                WaitingForOperationsSignal(
                    processor_id=self._id,
                    size_remaining=size_remaining,
                )
            )
        elif size_remaining:
            if self._backend_index is not None:
                self._logger.info(
                    WAITING_FOR_OPERATIONS_WITH_BACKEND_MSG,
                    self._backend_index,
                    size_remaining,
                )
            else:
                self._logger.info(
                    WAITING_FOR_OPERATIONS_MSG,
                    size_remaining,
                )

    def log_success(self, ops_synced: int) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                SuccessSignal(
                    processor_id=self._id,
                    ops_synced=ops_synced,
                    total_ops=self._total_ops,
                )
            )
        elif self._should_print_logs:
            if self._backend_index is not None:
                self._logger.info(SUCCESS_WITH_BACKEND_MSG, self._backend_index, ops_synced, self._total_ops)
            else:
                self._logger.info(SUCCESS_MSG, ops_synced, self._total_ops)

    def log_sync_failure(self, seconds: float, size_remaining: int) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                SyncFailureSignal(
                    processor_id=self._id,
                    seconds=seconds,
                    size_remaining=size_remaining,
                )
            )
        elif self._should_print_logs:
            if self._backend_index is not None:
                self._logger.warning(
                    SYNC_FAILURE_WITH_BACKEND_MSG,
                    self._backend_index,
                    seconds,
                    size_remaining,
                    self._data_path,
                )
            else:
                self._logger.warning(
                    SYNC_FAILURE_MSG,
                    seconds,
                    size_remaining,
                    self._data_path,
                )

    def log_reconnect_failure(self, max_reconnect_wait_time: float, size_remaining: int) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                ReconnectFailureSignal(
                    processor_id=self._id,
                    max_reconnect_wait_time=max_reconnect_wait_time,
                    size_remaining=size_remaining,
                )
            )
        elif self._should_print_logs:
            if self._backend_index is not None:
                self._logger.warning(
                    RECONNECT_FAILURE_WITH_BACKEND_MSG,
                    self._backend_index,
                    max_reconnect_wait_time,
                    size_remaining,
                    self._data_path,
                )
            else:
                self._logger.warning(
                    RECONNECT_FAILURE_MSG,
                    max_reconnect_wait_time,
                    size_remaining,
                    self._data_path,
                )

    def log_still_waiting(
        self, size_remaining: int, already_synced: int, already_synced_proc: float, is_disconnected: bool = False
    ) -> None:
        if self._signal_queue is not None:
            self._signal_queue.put(
                StillWaitingSignal(
                    processor_id=self._id,
                    size_remaining=size_remaining,
                    already_synced=already_synced,
                    already_synced_proc=already_synced_proc,
                )
            )
        elif self._should_print_logs:
            if self._backend_index is not None:
                msg = STILL_WAITING_DISCONNECTED_WITH_BACKEND_MSG if is_disconnected else STILL_WAITING_WITH_BACKEND_MSG
                self._logger.info(
                    msg,
                    self._backend_index,
                    size_remaining,
                    already_synced_proc,
                )
            else:
                msg = STILL_WAITING_DISCONNECTED_MSG if is_disconnected else STILL_WAITING_MSG
                self._logger.info(
                    msg,
                    size_remaining,
                    already_synced_proc,
                )
