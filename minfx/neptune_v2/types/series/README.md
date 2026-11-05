# series

Value type classes for series attributes in Neptune.

## Purpose

This module defines data classes representing different types of series
values that can be logged to Neptune.
[`Series`] is the base class for all series value types.
[`FloatSeries`] stores floating-point series values.
[`StringSeries`] stores string series values.
[`FileSeries`] stores file series values.
[`SeriesValue`] wraps individual step, value, and timestamp entries.
These value types support time-series data with timestamps.
They provide type-safe value containers and batch operations.
They also support serialization for backend transmission.
[`FloatSeries`] supports IEEE 754 special values including [`float("nan")`],
[`float("inf")`], [`float("-inf")`], and [`-0.0`].
These are encoded as strings during JSON serialization and decoded
transparently by the backend.

## Subdirectories / Files

- `./__init__.py` - Public exports for [`FloatSeries`], [`StringSeries`], and
  [`FileSeries`].
- `./file_series.py` - [`FileSeries`] for file series value types.
- `./float_series.py` - [`FloatSeries`] for floating-point series values.
- `./series.py` - [`Series`] abstract base for series value types.
- `./series_value.py` - [`SeriesValue`] wrapper for step, value, and
  timestamp tuples.
- `./string_series.py` - [`StringSeries`] for string series value types.

## Usages

- Use [`FloatSeries`] to represent floating-point metric value containers.
- Use [`StringSeries`] to represent string log line value containers.
- Use [`FileSeries`] to represent file attachment value containers.
- Use [`SeriesValue`] for individual series entries with step and timestamp
  metadata.
- Users typically interact with these types indirectly through series logging
  methods.
- See [`../README.md`] for the parent types module overview.


[`Series`]: series.Series
[`FloatSeries`]: float_series.FloatSeries
[`StringSeries`]: string_series.StringSeries
[`FileSeries`]: file_series.FileSeries
[`SeriesValue`]: series_value.SeriesValue
[`float("nan")`]: float_series.py
[`float("inf")`]: float_series.py
[`float("-inf")`]: float_series.py
[`-0.0`]: float_series.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
