# series

Series (time-series) attribute types for Neptune experiments.

## Purpose

This module provides series attribute types for logging time-varying data.
[`Series`] represents sequences of values logged over time, such as training
metrics or system metrics.
[`Series`] is the base class for all series attributes with batch logging
support.
[`FloatSeries`] stores floating-point metric values over time.
[`StringSeries`] stores string log lines over time.
[`FileSeries`] stores file attachments in a time series.
[`FetchableSeries`] is the base class for series that support fetching
historical values.
Series attributes support appending values with timestamps and batch logging.
They also support fetching historical values and step-based indexing.
[`FileSeries`] routes downloads across image, HTML, and generic file backends.

## Subdirectories / Files

- `./__init__.py` - Public exports for [`FloatSeries`], [`StringSeries`], and
  [`FileSeries`].
- `./fetchable_series.py` - [`FetchableSeries`] base for fetchable series
  types.
- `./file_series.py` - [`FileSeries`] for time-series file attachments.
- `./float_series.py` - [`FloatSeries`] for floating-point metric logging.
- `./series.py` - [`Series`] abstract base with batch logging support.
- `./string_series.py` - [`StringSeries`] for string log sequences.

## Usages

- Log training metrics with [`FloatSeries`] append and extend operations.
- Append string log lines with [`StringSeries`].
- Attach files over time with [`FileSeries`].
- Fetch historical values through [`FetchableSeries`] implementations.
- See [`../README.md`] for the parent attributes module overview.


[`Series`]: series.Series
[`FloatSeries`]: float_series.FloatSeries
[`StringSeries`]: string_series.StringSeries
[`FileSeries`]: file_series.FileSeries
[`FetchableSeries`]: fetchable_series.FetchableSeries
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
