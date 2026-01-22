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

__all__ = ["FileSeries"]

from itertools import cycle
import time
from typing import (
    TYPE_CHECKING,
    Sequence,
    TypeVar,
)

from minfx.neptune_v2.internal.types.stringify_value import extract_if_stringify_value
from minfx.neptune_v2.internal.utils import is_collection
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.types import File
from minfx.neptune_v2.types.series.series import Series

if TYPE_CHECKING:
    from minfx.neptune_v2.types.value_visitor import ValueVisitor

logger = get_logger()
Ret = TypeVar("Ret")


from typing import Iterable


class FileSeries(Series):
    def __init__(
        self,
        values: Iterable[File],
        timestamps: Sequence[float] | None = None,
        steps: Sequence[float] | None = None,
        **kwargs: str,
    ) -> None:
        values = extract_if_stringify_value(values)

        if not is_collection(values):
            raise TypeError("`values` is not a collection")

        self._values = [File.create_from(value) for value in values]
        self.name = kwargs.pop("name", None)
        self.description = kwargs.pop("description", None)
        if kwargs:
            logger.error("Warning: unexpected arguments (%s) in FileSeries", kwargs)

        if steps is None:
            self._steps = cycle([None])
        else:
            assert len(values) == len(steps)
            self._steps = steps

        if timestamps is None:
            self._timestamps = cycle([time.time()])
        else:
            assert len(values) == len(timestamps)
            self._timestamps = timestamps

    @property
    def steps(self) -> Sequence[float | None]:
        return self._steps

    @property
    def timestamps(self) -> Sequence[float]:
        return self._timestamps

    def accept(self, visitor: ValueVisitor[Ret]) -> Ret:
        return visitor.visit_image_series(self)

    @property
    def values(self) -> list[File]:
        return self._values

    def __str__(self) -> str:
        return f"FileSeries({self.values})"
