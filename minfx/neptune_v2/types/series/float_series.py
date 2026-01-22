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

__all__ = ["FloatSeries"]

from itertools import cycle
import time
from typing import (
    TYPE_CHECKING,
    Callable,
    Iterable,
    Sequence,
    TypeVar,
)

from minfx.neptune_v2.common.warnings import (
    NeptuneUnsupportedValue,
    warn_once,
)
from minfx.neptune_v2.internal.types.stringify_value import extract_if_stringify_value
from minfx.neptune_v2.internal.types.utils import is_unsupported_float
from minfx.neptune_v2.internal.utils import is_collection
from minfx.neptune_v2.types.series.series import Series

if TYPE_CHECKING:
    from minfx.neptune_v2.types.value_visitor import ValueVisitor

Ret = TypeVar("Ret")


class FloatSeries(Series):
    def __init__(
        self,
        values: Iterable[float | int],
        min: float | None = None,
        max: float | None = None,
        unit: str | None = None,
        timestamps: Sequence[float] | None = None,
        steps: Sequence[float] | None = None,
    ) -> None:
        values = extract_if_stringify_value(values)

        if not is_collection(values):
            raise TypeError("`values` is not a collection")

        self._values = [float(value) for value in values]
        self._min = min
        self._max = max
        self._unit = unit

        if steps is None:
            filled_steps = cycle([None])
        else:
            assert len(values) == len(steps)
            filled_steps = steps

        if timestamps is None:
            filled_timestamps = cycle([time.time()])
        else:
            assert len(values) == len(timestamps)
            filled_timestamps = timestamps

        clean_values, self._steps, self._timestamps = self.filter_unsupported_values(
            values=values,
            steps=filled_steps,
            timestamps=filled_timestamps,
            filter_by=self.is_unsupported_float_with_warn,
        )
        self._values = [float(value) for value in clean_values]

    @property
    def steps(self) -> list[float | None]:
        return self._steps

    @property
    def timestamps(self) -> list[float]:
        return self._timestamps

    def accept(self, visitor: ValueVisitor[Ret]) -> Ret:
        return visitor.visit_float_series(self)

    @property
    def values(self) -> list[float]:
        return self._values

    @property
    def min(self) -> float | None:
        return self._min

    @property
    def max(self) -> float | None:
        return self._max

    @property
    def unit(self) -> str | None:
        return self._unit

    def __str__(self) -> str:
        return f"FloatSeries({self.values!s})"

    def is_unsupported_float_with_warn(self, value: float) -> bool:
        if is_unsupported_float(value):
            warn_once(
                message=f"WARNING: A value you're trying to log (`{value!s}`) will be skipped because "
                f"it's a non-standard float value that is not currently supported.",
                exception=NeptuneUnsupportedValue,
            )
            return False
        return True

    def filter_unsupported_values(
        self,
        values: Iterable[float],
        steps: Iterable[float | None],
        timestamps: Iterable[float],
        filter_by: Callable[[float], bool],
    ) -> tuple[list[float], list[float | None], list[float]]:
        filtered = [
            (value, step, timestamp) for value, step, timestamp in zip(values, steps, timestamps) if filter_by(value)
        ]
        return (
            [value for value, _, _ in filtered],
            [step for _, step, _ in filtered],
            [timestamp for _, _, timestamp in filtered],
        )
