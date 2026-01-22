#
# Copyright (c) 2024, Neptune Labs Sp. z o.o.
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

__all__ = ["FileEntry"]

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    import datetime


@runtime_checkable
class FileEntryDTO(Protocol):
    """Protocol for file entry DTO from backend."""

    @property
    def name(self) -> str: ...
    @property
    def size(self) -> int: ...
    @property
    def mtime(self) -> datetime.datetime: ...
    @property
    def fileType(self) -> str: ...


@dataclass
class FileEntry:
    name: str
    size: int
    mtime: datetime.datetime
    file_type: str

    @classmethod
    def from_dto(cls, file_dto: FileEntryDTO) -> FileEntry:
        return cls(name=file_dto.name, size=file_dto.size, mtime=file_dto.mtime, file_type=file_dto.fileType)
