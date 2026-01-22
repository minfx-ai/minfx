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

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from minfx.neptune_v2.internal.types.stringify_value import extract_if_stringify_value
from minfx.neptune_v2.types.atoms.atom import Atom

if TYPE_CHECKING:
    from minfx.neptune_v2.types.value_visitor import ValueVisitor

Ret = TypeVar("Ret")


@dataclass
class Boolean(Atom):
    value: bool

    def __init__(self, value: bool | int) -> None:
        self.value = bool(extract_if_stringify_value(value))

    def accept(self, visitor: ValueVisitor[Ret]) -> Ret:
        return visitor.visit_boolean(self)

    def __str__(self) -> str:
        return f"Boolean({self.value!s})"

    def __bool__(self) -> bool:
        return self.value
