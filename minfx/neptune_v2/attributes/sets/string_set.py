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

__all__ = ["StringSet"]

from typing import (
    Iterable,
)

from minfx.neptune_v2.attributes.sets.set import Set
from minfx.neptune_v2.internal.operation import (
    AddStrings,
    ClearStringSet,
    RemoveStrings,
)
from minfx.neptune_v2.internal.utils import (
    is_collection,
    verify_collection_type,
    verify_type,
)
from minfx.neptune_v2.types.sets.string_set import StringSet as StringSetVal


class StringSet(Set):
    def assign(self, value: StringSetVal | Iterable[str], *, wait: bool = False):
        # Accept both StringSetVal and plain list/set/tuple of strings
        if isinstance(value, StringSetVal):
            values = value.values
        elif is_collection(value):
            verify_collection_type("value", value, str)
            values = set(value)
        else:
            verify_type("value", value, (StringSetVal, list, set, tuple))
            return  # unreachable, but satisfies type checker

        with self._container.lock():
            if not values:
                self._enqueue_operation(ClearStringSet(self._path), wait=wait)
            else:
                self._enqueue_operation(ClearStringSet(self._path), wait=False)
                self._enqueue_operation(AddStrings(self._path, values), wait=wait)

    def add(self, values: str | Iterable[str], *, wait: bool = False):
        values = self._to_proper_value_type(values)
        with self._container.lock():
            self._enqueue_operation(AddStrings(self._path, set(values)), wait=wait)

    def remove(self, values: str | Iterable[str], *, wait: bool = False):
        values = self._to_proper_value_type(values)
        with self._container.lock():
            self._enqueue_operation(RemoveStrings(self._path, set(values)), wait=wait)

    def clear(self, *, wait: bool = False):
        with self._container.lock():
            self._enqueue_operation(ClearStringSet(self._path), wait=wait)

    def fetch(self) -> set[str]:
        val = self._backend.get_string_set_attribute(self._container_id, self._container_type, self._path)
        return val.values

    @staticmethod
    def _to_proper_value_type(values: str | Iterable[str]) -> Iterable[str]:
        if is_collection(values):
            verify_collection_type("values", values, str)
            return list(values)
        verify_type("values", values, str)
        return [values]
