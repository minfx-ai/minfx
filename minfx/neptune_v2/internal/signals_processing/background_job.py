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

__all__ = ["CallbacksMonitor"]

from typing import (
    TYPE_CHECKING,
    Callable,
)

from minfx.neptune_v2.internal.background_job import BackgroundJob
from minfx.neptune_v2.internal.signals_processing.signals_processor import SignalsProcessor

if TYPE_CHECKING:
    from queue import Queue

    from minfx.neptune_v2.internal.signals_processing.signals import Signal
    from minfx.neptune_v2.metadata_containers import MetadataContainer


class CallbacksMonitor(BackgroundJob):
    def __init__(
        self,
        queue: Queue[Signal],
        async_lag_threshold: float,
        async_no_progress_threshold: float,
        async_lag_callback: Callable[[MetadataContainer], None] | None = None,
        async_no_progress_callback: Callable[[MetadataContainer], None] | None = None,
        period: float = 10,
    ) -> None:
        self._period: float = period
        self._queue: Queue[Signal] = queue
        self._thread: SignalsProcessor | None = None
        self._started: bool = False
        self._async_lag_threshold: float = async_lag_threshold
        self._async_no_progress_threshold: float = async_no_progress_threshold
        self._async_lag_callback: Callable[[MetadataContainer], None] | None = async_lag_callback
        self._async_no_progress_callback: Callable[[MetadataContainer], None] | None = async_no_progress_callback

    def start(self, container: MetadataContainer) -> None:
        self._thread = SignalsProcessor(
            period=self._period,
            container=container,
            queue=self._queue,
            async_lag_threshold=self._async_lag_threshold,
            async_no_progress_threshold=self._async_no_progress_threshold,
            async_lag_callback=self._async_lag_callback,
            async_no_progress_callback=self._async_no_progress_callback,
        )
        self._thread.start()
        self._started = True

    def stop(self) -> None:
        if self._thread and self._started:
            self._thread.interrupt()

    def join(self, seconds: float | None = None) -> None:
        if self._thread and self._started:
            self._thread.join(seconds)

    def pause(self) -> None:
        if self._thread:
            self._thread.pause()

    def resume(self) -> None:
        if self._thread:
            self._thread.resume()
