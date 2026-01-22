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
__all__ = ["Integer"]

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
class Integer(Atom):
    value: int

    def __init__(self, value: int) -> None:
        self.value = int(extract_if_stringify_value(value))

    def accept(self, visitor: "ValueVisitor[Ret]") -> Ret:
        return visitor.visit_integer(self)

    def __str__(self) -> str:
        return f"Integer({self.value!s})"

    def __int__(self) -> int:
        return self.value
