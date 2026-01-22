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

from typing import (
    Collection,
    Iterable,
    Union,
)

from minfx.neptune_v2.attributes.series.fetchable_series import FetchableSeries
from minfx.neptune_v2.attributes.series.series import Series
from minfx.neptune_v2.internal.backends.api_model import FloatSeriesValues
from minfx.neptune_v2.internal.operation import (
    ClearFloatLog,
    ConfigFloatSeries,
    LogFloats,
    Operation,
)
from minfx.neptune_v2.internal.utils import verify_type
from minfx.neptune_v2.types.series.float_series import FloatSeries as FloatSeriesVal

Val = FloatSeriesVal
Data = Union[float, int]
LogOperation = LogFloats


class FloatSeries(
    Series[Val, Data, LogOperation], FetchableSeries[FloatSeriesValues], max_batch_size=100, operation_cls=LogOperation
):
    def configure(
        self,
        min: float | None = None,
        max: float | None = None,
        unit: str | None = None,
        wait: bool = False,
    ) -> None:
        verify_type("min", min, (float, int))
        verify_type("max", max, (float, int))
        verify_type("unit", unit, str)
        with self._container.lock():
            self._enqueue_operation(ConfigFloatSeries(self._path, min, max, unit), wait=wait)

    def _get_clear_operation(self) -> Operation:
        return ClearFloatLog(self._path)

    def _get_config_operation_from_value(self, value: Val) -> Operation | None:
        return ConfigFloatSeries(self._path, value.min, value.max, value.unit)

    def _data_to_value(
        self,
        values: Iterable[float | int],
        steps: Collection[float] | None = None,
        timestamps: Collection[float] | None = None,
    ) -> Val:
        return FloatSeriesVal(values, steps=steps, timestamps=timestamps)

    def _is_value_type(self, value: object) -> bool:
        # Accept minfx FloatSeriesVal or any duck-typed series with required attrs
        # This handles Neptune SDK's FloatSeries (neptune.types.series.float_series.FloatSeries)
        if isinstance(value, FloatSeriesVal):
            return True
        # Duck typing: check if it has the required series attributes
        return hasattr(value, "values") and hasattr(value, "steps") and hasattr(value, "timestamps")

    def fetch_last(self) -> float:
        val = self._backend.get_float_series_attribute(self._container_id, self._container_type, self._path)
        return val.last

    def _fetch_values_from_backend(self, offset: int, limit: int) -> FloatSeriesValues:
        return self._backend.get_float_series_values(
            self._container_id, self._container_type, self._path, offset, limit
        )
