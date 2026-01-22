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

__all__ = ["cast_value", "cast_value_for_extend"]

import argparse
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Collection,
    Mapping,
)

from minfx.neptune_v2.internal.utils import (
    is_bool,
    is_dict_like,
    is_float,
    is_float_like,
    is_int,
    is_string,
    is_stringify_value,
)
from minfx.neptune_v2.types import (
    Boolean,
    File,
    Integer,
)
from minfx.neptune_v2.types.atoms.datetime import Datetime
from minfx.neptune_v2.types.atoms.float import Float
from minfx.neptune_v2.types.atoms.string import String
from minfx.neptune_v2.types.namespace import Namespace
from minfx.neptune_v2.types.series import (
    FileSeries,
    FloatSeries,
    StringSeries,
)
from minfx.neptune_v2.types.series.series import Series
from minfx.neptune_v2.types.value import Value
from minfx.neptune_v2.types.value_copy import ValueCopy

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.types.stringify_value import StringifyValue

# Type alias for values that can be cast
CastableValue = Value | bool | int | float | str | datetime | dict | Mapping | argparse.Namespace | object


def _is_neptune_sdk_series(value: object) -> bool:
    """Check if value is a Neptune SDK series type (duck typing).

    Neptune SDK's FloatSeries/StringSeries have: values, steps, timestamps.
    This allows minfx to accept neptune.types.FloatSeries/StringSeries.
    """
    return (
        hasattr(value, "values")
        and hasattr(value, "steps")
        and hasattr(value, "timestamps")
        and not isinstance(value, Value)  # Not already a minfx Value
    )


def _extract_series_attr(value: object, attr_name: str, values_len: int) -> list | None:
    """Extract a series attribute, converting iterators to lists if needed.

    Neptune SDK uses cycle() for timestamps/steps when not explicitly provided.
    We need to convert these to proper lists for minfx.
    """
    attr = getattr(value, attr_name, None)
    if attr is None:
        return None
    # If it's already a list with the right length, use it
    if isinstance(attr, list) and len(attr) == values_len:
        return attr
    # If it's an iterator (like cycle), materialize it
    try:
        # Take exactly values_len items from the iterator
        result = []
        attr_iter = iter(attr)
        for _ in range(values_len):
            result.append(next(attr_iter))
        return result
    except (TypeError, StopIteration):
        return None


def _convert_neptune_sdk_series(value: object) -> Value | None:
    """Convert Neptune SDK series to minfx series."""
    # Check if it's a float series by looking at values
    values = getattr(value, "values", [])
    values_len = len(values) if values else 0

    if not values:
        # Empty series - try to determine type from class name
        type_name = type(value).__name__.lower()
        if "string" in type_name:
            return StringSeries(values=[])
        return FloatSeries(
            values=[],
            min=getattr(value, "min", None),
            max=getattr(value, "max", None),
            unit=getattr(value, "unit", None),
        )

    # Extract steps and timestamps, handling iterators
    steps = _extract_series_attr(value, "steps", values_len)
    timestamps = _extract_series_attr(value, "timestamps", values_len)

    # Check first value to determine type
    first_val = values[0]
    if isinstance(first_val, str):
        return StringSeries(
            values=values,
            steps=steps,
            timestamps=timestamps,
        )
    return FloatSeries(
        values=values,
        steps=steps,
        timestamps=timestamps,
        min=getattr(value, "min", None),
        max=getattr(value, "max", None),
        unit=getattr(value, "unit", None),
    )


def cast_value(value: CastableValue) -> Value | None:
    from minfx.neptune_v2.handler import Handler

    from_stringify_value = False
    if is_stringify_value(value):
        from_stringify_value, value = True, value.value  # type: ignore[union-attr]

    if isinstance(value, Value):
        return value
    # Handle Neptune SDK series types (neptune.types.FloatSeries/StringSeries)
    if _is_neptune_sdk_series(value):
        return _convert_neptune_sdk_series(value)
    if isinstance(value, Handler):
        return ValueCopy(value)
    if isinstance(value, argparse.Namespace):
        return Namespace(vars(value))
    if File.is_convertable_to_image(value):
        return File.as_image(value)
    if File.is_convertable_to_html(value):
        return File.as_html(value)
    if is_bool(value):
        return Boolean(value)
    if is_int(value):
        return Integer(value)
    if is_float(value):
        return Float(value)
    if is_string(value):
        return String(value)
    if isinstance(value, datetime):
        return Datetime(value)
    if is_float_like(value):
        return Float(value)
    if is_dict_like(value):
        return Namespace(value)
    if from_stringify_value:
        return String(str(value))
    return None


def cast_value_for_extend(values: StringifyValue | Namespace | Series | Collection[Any]) -> Series | Namespace | None:
    from_stringify_value, original_values = False, None
    if is_stringify_value(values):
        from_stringify_value, original_values, values = True, values, values.value

    if isinstance(values, Namespace):
        return values
    if is_dict_like(values):
        return Namespace(values)
    if isinstance(values, Series):
        return values

    sample_val = next(iter(values))

    if (
        isinstance(sample_val, File)
        or File.is_convertable_to_image(sample_val)
        or File.is_convertable_to_html(sample_val)
    ):
        return FileSeries(values=values)
    if is_string(sample_val):
        return StringSeries(values=values)
    if is_float_like(sample_val):
        return FloatSeries(values=values)
    if from_stringify_value:
        return StringSeries(values=original_values)
    return None
