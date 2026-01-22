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

__all__ = ["Boolean"]

import typing

from minfx.neptune_v2.attributes.atoms.copiable_atom import CopiableAtom
from minfx.neptune_v2.internal.operation import AssignBool
from minfx.neptune_v2.types.atoms.boolean import Boolean as BooleanVal

if typing.TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType


class Boolean(CopiableAtom):
    @staticmethod
    def create_assignment_operation(path: list[str], value: bool) -> AssignBool:
        return AssignBool(path, value)

    @staticmethod
    def getter(
        backend: NeptuneBackend,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
    ) -> bool:
        val = backend.get_bool_attribute(container_id, container_type, path)
        return val.value

    def assign(self, value: BooleanVal | bool, *, wait: bool = False):
        if not isinstance(value, BooleanVal):
            value = BooleanVal(value)

        with self._container.lock():
            self._enqueue_operation(self.create_assignment_operation(self._path, value.value), wait=wait)
