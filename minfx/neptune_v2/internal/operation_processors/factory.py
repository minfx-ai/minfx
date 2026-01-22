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

__all__ = ["get_operation_processor"]

import os
import threading
from typing import TYPE_CHECKING

from minfx.neptune_v2.envs import NEPTUNE_ASYNC_BATCH_SIZE
from minfx.neptune_v2.internal.backends.multi_backend import MultiBackend
from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
from minfx.neptune_v2.internal.container_type import ContainerType
from minfx.neptune_v2.internal.id_formats import UniqueId
from minfx.neptune_v2.types.mode import Mode

from .async_operation_processor import AsyncOperationProcessor
from .multi_backend_operation_processor import MultiBackendOperationProcessor
from .offline_operation_processor import OfflineOperationProcessor
from .operation_processor import OperationProcessor
from .read_only_operation_processor import ReadOnlyOperationProcessor
from .sync_operation_processor import SyncOperationProcessor

if TYPE_CHECKING:
    from queue import Queue

    from minfx.neptune_v2.internal.signals_processing.signals import Signal


# WARNING: Be careful when changing this function. It is used in the experimental package
def build_async_operation_processor(
    container_id: UniqueId,
    container_type: ContainerType,
    backend: NeptuneBackend,
    lock: threading.RLock,
    sleep_time: float,
    queue: "Queue[Signal]",
) -> OperationProcessor:
    # Backend is always a MultiBackend now (even for single-backend configs)
    # MultiBackendOperationProcessor handles both single and multi-backend cases
    assert isinstance(backend, MultiBackend), "Backend must be a MultiBackend"
    return MultiBackendOperationProcessor(
        container_id=container_id,
        container_type=container_type,
        multi_backend=backend,
        lock=lock,
        queue=queue,
        sleep_time=sleep_time,
        batch_size=int(os.environ.get(NEPTUNE_ASYNC_BATCH_SIZE) or "2048"),
    )


def get_operation_processor(
    mode: Mode,
    container_id: UniqueId,
    container_type: ContainerType,
    backend: NeptuneBackend,
    lock: threading.RLock,
    flush_period: float,
    queue: "Queue[Signal]",
) -> OperationProcessor:
    if mode == Mode.ASYNC:
        return build_async_operation_processor(
            container_id=container_id,
            container_type=container_type,
            backend=backend,
            lock=lock,
            sleep_time=flush_period,
            queue=queue,
        )
    if mode in (Mode.SYNC, Mode.DEBUG):
        return SyncOperationProcessor(container_id, container_type, backend)
    if mode == Mode.OFFLINE:
        # the object was returned by mocked backend and has some random ID.
        return OfflineOperationProcessor(container_id, container_type, lock)
    if mode == Mode.READ_ONLY:
        return ReadOnlyOperationProcessor()
    raise ValueError(f"mode should be one of {list(Mode)}")
