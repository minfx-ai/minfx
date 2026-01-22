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

__all__ = ["Attribute"]

from typing import (
    TYPE_CHECKING,
)

from minfx.neptune_v2.exceptions import TypeDoesNotSupportAttributeException
from minfx.neptune_v2.types.value_copy import ValueCopy

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.operation import Operation
    from minfx.neptune_v2.metadata_containers import MetadataContainer


class Attribute:
    supports_copy = False

    def __init__(self, container: MetadataContainer, path: list[str]):
        super().__init__()
        self._container = container
        self._path = path

    def __getattr__(self, attr: str) -> None:
        raise TypeDoesNotSupportAttributeException(type_=type(self), attribute=attr)

    def _enqueue_operation(self, operation: Operation, *, wait: bool):
        self._container._op_processor.enqueue_operation(operation, wait=wait)

    @property
    def _backend(self) -> NeptuneBackend:
        return self._container._backend

    @property
    def _container_id(self) -> str:
        return self._container._id

    @property
    def _container_type(self) -> ContainerType:
        return self._container.container_type

    def copy(self, value: ValueCopy, wait: bool = False):
        raise Exception(f"{type(self).__name__} doesn't support copying")

    def process_assignment(self, value: object, wait: bool = False) -> None:
        if isinstance(value, ValueCopy):
            return self.copy(value, wait=wait)
        return self.assign(value, wait=wait)
