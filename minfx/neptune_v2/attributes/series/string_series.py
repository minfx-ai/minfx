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

__all__ = ["StringSeries"]

from typing import (
    TYPE_CHECKING,
    Collection,
    Iterable,
)

from minfx.neptune_v2.attributes.series.fetchable_series import FetchableSeries
from minfx.neptune_v2.attributes.series.series import Series
from minfx.neptune_v2.internal.backends.api_model import StringSeriesValues
from minfx.neptune_v2.internal.operation import (
    ClearStringLog,
    LogStrings,
    Operation,
)
from minfx.neptune_v2.internal.types.stringify_value import StringifyValue
from minfx.neptune_v2.internal.utils import is_collection
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.paths import path_to_str
from minfx.neptune_v2.types.series.string_series import MAX_STRING_SERIES_VALUE_LENGTH, StringSeries as StringSeriesVal

if TYPE_CHECKING:
    from minfx.neptune_v2.metadata_containers import MetadataContainer

Val = StringSeriesVal
Data = str
LogOperation = LogStrings

logger = get_logger()


class StringSeries(
    Series[Val, Data, LogOperation], FetchableSeries[StringSeriesValues], max_batch_size=10, operation_cls=LogOperation
):
    def __init__(self, container: MetadataContainer, path: list[str]):
        super().__init__(container, path)
        self._value_truncation_occurred = False

    def _get_log_operations_from_value(
        self,
        value: Val,
    ) -> list[LogOperation]:
        if not self._value_truncation_occurred and value.truncated:
            # the first truncation
            self._value_truncation_occurred = True
            logger.warning(
                "Warning: string series '%s' value was"
                " longer than %s characters and was truncated."
                " This warning is printed only once per series.",
                path_to_str(self._path),
                MAX_STRING_SERIES_VALUE_LENGTH,
            )

        return super()._get_log_operations_from_value(value)

    def _get_clear_operation(self) -> Operation:
        return ClearStringLog(self._path)

    def _data_to_value(
        self,
        values: Iterable[str],
        steps: Collection[float] | None = None,
        timestamps: Collection[float] | None = None,
    ) -> Val:
        return StringSeriesVal(values, steps=steps, timestamps=timestamps)

    def _is_value_type(self, value: object) -> bool:
        # Accept minfx StringSeriesVal or any duck-typed series with required attrs
        # This handles Neptune SDK's StringSeries (neptune.types.series.string_series.StringSeries)
        if isinstance(value, StringSeriesVal):
            return True
        # Duck typing: check if it has the required series attributes
        return hasattr(value, "values") and hasattr(value, "steps") and hasattr(value, "timestamps")

    def _handle_stringified_value(self, value: StringifyValue) -> list[str] | str:
        if is_collection(value.value):
            return list(map(str, value.value))
        return str(value.value)

    def fetch_last(self) -> str:
        val = self._backend.get_string_series_attribute(self._container_id, self._container_type, self._path)
        return val.last

    def _fetch_values_from_backend(self, offset: int, limit: int) -> StringSeriesValues:
        return self._backend.get_string_series_values(
            self._container_id, self._container_type, self._path, offset, limit
        )
