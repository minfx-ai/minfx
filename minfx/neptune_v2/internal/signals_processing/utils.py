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

__all__ = ["signal_batch_lag", "signal_batch_processed", "signal_batch_started"]

from queue import (
    Full,
    Queue,
)
from time import monotonic

from minfx.neptune_v2.common.warnings import (
    NeptuneWarning,
    warn_once,
)
from minfx.neptune_v2.internal.signals_processing.signals import (
    BatchLagSignal,
    BatchProcessedSignal,
    BatchStartedSignal,
    Signal,
)


def signal(*, queue: Queue[Signal], obj: Signal) -> None:
    try:
        queue.put_nowait(item=obj)
    except Full:
        warn_once("Signal queue is full. Some signals will be lost.", exception=NeptuneWarning)


def signal_batch_started(*, queue: Queue[Signal], occured_at: float | None = None) -> None:
    signal(queue=queue, obj=BatchStartedSignal(occured_at=occured_at or monotonic()))


def signal_batch_processed(*, queue: Queue[Signal], occured_at: float | None = None) -> None:
    signal(queue=queue, obj=BatchProcessedSignal(occured_at=occured_at or monotonic()))


def signal_batch_lag(*, queue: Queue[Signal], lag: float, occured_at: float | None = None) -> None:
    signal(queue=queue, obj=BatchLagSignal(occured_at=occured_at or monotonic(), lag=lag))
