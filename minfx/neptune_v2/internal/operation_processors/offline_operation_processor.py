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

__all__ = ("OfflineOperationProcessor",)

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

from minfx.neptune_v2.constants import OFFLINE_DIRECTORY
from minfx.neptune_v2.core.components.abstract import WithResources
from minfx.neptune_v2.core.components.metadata_file import MetadataFile
from minfx.neptune_v2.core.components.operation_storage import OperationStorage
from minfx.neptune_v2.core.components.queue.disk_queue import DiskQueue
from minfx.neptune_v2.internal.operation import Operation
from minfx.neptune_v2.internal.operation_processors.operation_processor import OperationProcessor
from minfx.neptune_v2.internal.operation_processors.utils import (
    common_metadata,
    get_container_full_path,
)
from minfx.neptune_v2.internal.utils.disk_utilization import ensure_disk_not_overutilize

if TYPE_CHECKING:
    import threading

    from minfx.neptune_v2.core.components.abstract import Resource
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import UniqueId


def serializer(op: Operation) -> dict[str, Any]:
    return op.to_dict()


class OfflineOperationProcessor(WithResources, OperationProcessor):
    def __init__(self, container_id: UniqueId, container_type: ContainerType, lock: threading.RLock):
        self._data_path = get_container_full_path(OFFLINE_DIRECTORY, container_id, container_type)

        # Initialize directory
        self._data_path.mkdir(parents=True, exist_ok=True)

        self._metadata_file = MetadataFile(
            data_path=self._data_path,
            metadata=common_metadata(mode="offline", container_id=container_id, container_type=container_type),
        )
        self._operation_storage = OperationStorage(data_path=self._data_path)
        self._queue = DiskQueue(data_path=self._data_path, to_dict=serializer, from_dict=Operation.from_dict, lock=lock)

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
        self._queue.put(op)

    def wait(self) -> None:
        self.flush()

    def stop(self, seconds: float | None = None) -> None:
        self.flush()
        self.close()
