#
# Copyright (c) 2023, Neptune Labs Sp. z o.o.
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

__all__ = ["SignalsProcessor"]

from queue import (
    Empty,
    Queue,
)
from threading import Thread
from time import monotonic
from typing import (
    TYPE_CHECKING,
    Callable,
)

from minfx.neptune_v2.internal.init.parameters import IN_BETWEEN_CALLBACKS_MINIMUM_INTERVAL
from minfx.neptune_v2.internal.signals_processing.signals import (
    BatchLagSignal,
    SignalsVisitor,
)
from minfx.neptune_v2.internal.threading.daemon import Daemon

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.signals_processing.signals import Signal
    from minfx.neptune_v2.metadata_containers import MetadataContainer


class SignalsProcessor(Daemon, SignalsVisitor):
    def __init__(
        self,
        *,
        period: float,
        container: MetadataContainer,
        queue: Queue[Signal],
        async_lag_threshold: float,
        async_no_progress_threshold: float,
        async_lag_callback: Callable[[MetadataContainer], None] | None = None,
        async_no_progress_callback: Callable[[MetadataContainer], None] | None = None,
        callbacks_interval: float = IN_BETWEEN_CALLBACKS_MINIMUM_INTERVAL,
        in_async: bool = True,
    ) -> None:
        super().__init__(sleep_time=period, name="CallbacksMonitor")

        self._container: MetadataContainer = container
        self._queue: Queue[Signal] = queue
        self._async_lag_threshold: float = async_lag_threshold
        self._async_no_progress_threshold: float = async_no_progress_threshold
        self._async_lag_callback: Callable[[MetadataContainer], None] | None = async_lag_callback
        self._async_no_progress_callback: Callable[[MetadataContainer], None] | None = async_no_progress_callback
        self._callbacks_interval: float = callbacks_interval
        self._in_async: bool = in_async

        self._last_batch_started_at: float | None = None
        self._last_no_progress_callback_at: float | None = None
        self._last_lag_callback_at: float | None = None

    def visit_batch_started(self, signal: Signal) -> None:
        if self._last_batch_started_at is None:
            self._last_batch_started_at = signal.occured_at

    def visit_batch_processed(self, signal: Signal) -> None:
        if self._last_batch_started_at is not None:
            self._check_no_progress(at_timestamp=signal.occured_at)
            self._last_batch_started_at = None

    def visit_batch_lag(self, signal: Signal) -> None:
        if self._async_lag_callback is None or not isinstance(signal, BatchLagSignal):
            return

        if signal.lag > self._async_lag_threshold:
            current_time = monotonic()
            if (
                self._last_lag_callback_at is None
                or current_time - self._last_lag_callback_at > self._callbacks_interval
            ):
                execute_callback(callback=self._async_lag_callback, container=self._container, in_async=self._in_async)
                self._last_lag_callback_at = current_time

    def _check_callbacks(self) -> None:
        self._check_no_progress(at_timestamp=monotonic())

    def _check_no_progress(self, at_timestamp: float) -> None:
        if self._async_no_progress_callback is None:
            return

        if self._last_batch_started_at is not None:
            if at_timestamp - self._last_batch_started_at > self._async_no_progress_threshold and (
                self._last_no_progress_callback_at is None
                or at_timestamp - self._last_no_progress_callback_at > self._callbacks_interval
            ):
                execute_callback(
                    callback=self._async_no_progress_callback, container=self._container, in_async=self._in_async
                )
                self._last_no_progress_callback_at = monotonic()

    def work(self) -> None:
        try:
            while not self._queue.empty():
                signal = self._queue.get_nowait()
                signal.accept(self)
            self._check_callbacks()
        except Empty:
            pass


def execute_callback(
    *, callback: Callable[[MetadataContainer], None], container: MetadataContainer, in_async: bool
) -> None:
    if in_async:
        Thread(target=callback, name="CallbackExecution", args=(container,), daemon=True).start()
    else:
        callback(container)
