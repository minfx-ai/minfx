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

__all__ = ["Namespace"]

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.paths import parse_path
from minfx.neptune_v2.types.value import Value

if TYPE_CHECKING:
    from minfx.neptune_v2.types.value_visitor import ValueVisitor

logger = get_logger()
Ret = TypeVar("Ret")


@dataclass
class Namespace(Value):
    value: dict

    def __init__(self, value: dict[str, object]) -> None:
        self.value = value
        empty_keys = [k for k in self.value if not parse_path(k)]
        if empty_keys:
            all_keys = ", ".join(['"' + k + '"' for k in empty_keys])
            logger.warning(
                f"Key(s) {all_keys} can't be used in Namespaces and dicts stored in Neptune. Please use non-empty "
                f"keys instead. The value(s) will be dropped.",
            )
            self.value = value.copy()
            [self.value.pop(key) for key in empty_keys]

    def accept(self, visitor: ValueVisitor[Ret]) -> Ret:
        return visitor.visit_namespace(self)

    def __str__(self) -> str:
        return f"Namespace({self.value!s})"
