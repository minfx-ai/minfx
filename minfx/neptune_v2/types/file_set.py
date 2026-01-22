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

__all__ = [
    "FileSet",
]

from typing import (
    TYPE_CHECKING,
    Iterable,
    TypeVar,
)

from minfx.neptune_v2.internal.utils import (
    verify_collection_type,
    verify_type,
)
from minfx.neptune_v2.types.value import Value

if TYPE_CHECKING:
    from minfx.neptune_v2.types.value_visitor import ValueVisitor

Ret = TypeVar("Ret")


class FileSet(Value):
    def __init__(self, file_globs: str | Iterable[str]):
        verify_type("file_globs", file_globs, (str, Iterable))
        if isinstance(file_globs, str):
            file_globs = [file_globs]
        else:
            verify_collection_type("file_globs", file_globs, str)
        self.file_globs: list[str] = list(file_globs)

    def accept(self, visitor: ValueVisitor[Ret]) -> Ret:
        return visitor.visit_file_set(self)

    def __str__(self) -> str:
        return f"FileSet({self.file_globs!s})"
