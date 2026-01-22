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

__all__ = ["QualifiedName", "SysId", "UniqueId", "conform_optional"]

from typing import (
    Callable,
    NewType,
    TypeVar,
)

UniqueId = NewType("UniqueId", str)

SysId = NewType("SysId", str)

QualifiedName = NewType("QualifiedName", str)

T = TypeVar("T")


def conform_optional(value: str | None, cls: Callable[[str], T]) -> T | None:
    return cls(value) if value is not None else None
