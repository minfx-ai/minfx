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

__all__ = ["Datetime"]

from datetime import datetime
import typing

from minfx.neptune_v2.attributes.atoms.copiable_atom import CopiableAtom
from minfx.neptune_v2.internal.operation import AssignDatetime
from minfx.neptune_v2.internal.types.stringify_value import StringifyValue
from minfx.neptune_v2.internal.utils import verify_type
from minfx.neptune_v2.types.atoms.datetime import Datetime as DatetimeVal

if typing.TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType


class Datetime(CopiableAtom):
    @staticmethod
    def create_assignment_operation(path: list[str], value: datetime) -> AssignDatetime:
        return AssignDatetime(path, value)

    @staticmethod
    def getter(
        backend: NeptuneBackend,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
    ) -> datetime:
        val = backend.get_datetime_attribute(container_id, container_type, path)
        return val.value

    def assign(self, value: DatetimeVal | datetime | StringifyValue, *, wait: bool = False):
        verify_type("value", value, (DatetimeVal, datetime, StringifyValue))
        if isinstance(value, (DatetimeVal, StringifyValue)):
            value = value.value
        else:
            value = value.replace(microsecond=1000 * int(value.microsecond / 1000))
        with self._container.lock():
            self._enqueue_operation(self.create_assignment_operation(self._path, value), wait=wait)
