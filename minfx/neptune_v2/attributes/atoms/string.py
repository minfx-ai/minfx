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

__all__ = ["String"]

import typing

from minfx.neptune_v2.attributes.atoms.copiable_atom import CopiableAtom
from minfx.neptune_v2.internal.operation import AssignString
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.paths import path_to_str
from minfx.neptune_v2.types.atoms.string import String as StringVal

if typing.TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.metadata_containers import MetadataContainer

logger = get_logger()


class String(CopiableAtom):
    MAX_VALUE_LENGTH = 16384

    def __init__(self, container: MetadataContainer, path: list[str]):
        super().__init__(container, path)
        self._value_truncation_occurred = False

    @staticmethod
    def create_assignment_operation(path: list[str], value: str) -> AssignString:
        return AssignString(path, value)

    @staticmethod
    def getter(
        backend: NeptuneBackend,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
    ) -> str:
        val = backend.get_string_attribute(container_id, container_type, path)
        return val.value

    def assign(self, value: StringVal | str, *, wait: bool = False):
        if not isinstance(value, StringVal):
            value = StringVal(value)

        if len(value.value) > String.MAX_VALUE_LENGTH:
            value.value = value.value[: String.MAX_VALUE_LENGTH]

            if not self._value_truncation_occurred:
                # the first truncation
                self._value_truncation_occurred = True
                logger.warning(
                    "Warning: string '%s' value was"
                    " longer than %s characters and was truncated."
                    " This warning is printed only once.",
                    path_to_str(self._path),
                    String.MAX_VALUE_LENGTH,
                )

        with self._container.lock():
            self._enqueue_operation(self.create_assignment_operation(self._path, value.value), wait=wait)
