# Series Attributes

This module provides series (time-series) attribute types for Neptune experiments.

## Purpose

Series represent sequences of values logged over time, such as training metrics, system metrics, or any other time-varying data.

## Key Components

- `Series`: Base class for all series attributes with batch logging support
- `FloatSeries`: Time series of floating-point values
- `StringSeries`: Time series of string values
- `FileSeries`: Time series of file attachments
- `FetchableSeries`: Base class for series that support fetching historical values

## Functionality

Series attributes support:
- Appending values with timestamps
- Batch logging for efficiency
- Fetching historical values
- Automatic batching and buffering
- Step-based and time-based indexing
- FileSeries download routing across image/html/generic file backends

## Usage

Series are used to log metrics and other time-varying data:
```python
run["metrics/loss"].append(0.5)  # FloatSeries
run["metrics/accuracy"].extend([0.8, 0.85, 0.9])  # Batch logging
run["logs/output"].append("Training started")  # StringSeries
```

## Parent Module

See `../README.md` for information about the attributes system.

---
e5eef531 2026-03-02T09:34:16
