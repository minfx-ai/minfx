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

__all__ = ["CopiableAtom"]

import abc
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

from minfx.neptune_v2.attributes.atoms.atom import Atom
from minfx.neptune_v2.internal.operation import CopyAttribute
from minfx.neptune_v2.internal.utils.paths import parse_path

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.operation import Operation
    from minfx.neptune_v2.types.value_copy import ValueCopy

ValT = TypeVar("ValT")  # The value type (int, float, str, bool, datetime)
OpT = TypeVar("OpT", bound="Operation")


class CopiableAtom(Atom, Generic[ValT, OpT]):
    supports_copy = True

    def copy(self, value: ValueCopy, *, wait: bool = False) -> None:
        with self._container.lock():
            source_path = value.source_handler._path
            source_attr = value.source_handler._get_attribute()
            self._enqueue_operation(
                CopyAttribute(
                    self._path,
                    container_id=source_attr._container_id,
                    container_type=source_attr._container_type,
                    source_path=parse_path(source_path),
                    source_attr_cls=source_attr.__class__,
                ),
                wait=wait,
            )

    @staticmethod
    @abc.abstractmethod
    def create_assignment_operation(path: list[str], value: ValT) -> OpT: ...

    @staticmethod
    @abc.abstractmethod
    def getter(
        backend: NeptuneBackend,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
    ) -> ValT: ...

    def fetch(self) -> ValT:
        return self.getter(self._backend, self._container_id, self._container_type, self._path)
