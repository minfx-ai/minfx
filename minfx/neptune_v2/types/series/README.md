# Series Value Types

This module provides value type classes for series attributes.

## Purpose

The series value types module defines the data classes representing different types of series values that can be logged to Neptune.

## Key Components

- `Series`: Base class for all series value types
- `FloatSeries`: Floating-point series value type
- `StringSeries`: String series value type
- `FileSeries`: File series value type
- `series_value.py`: Series value wrapper classes

## Functionality

These value types:
- Represent different data types for series values
- Support time-series data with timestamps
- Provide type-safe value containers
- Enable batch operations
- Support serialization for backend transmission

## Special Float Values

`FloatSeries` supports IEEE 754 special values:
- `float("nan")` - NaN values
- `float("inf")` - Positive infinity
- `float("-inf")` - Negative infinity
- `-0.0` - Negative zero

These are encoded as strings during JSON serialization and decoded transparently by the backend.

## Usage

These types are used internally to represent values logged to series attributes. Users typically don't interact with these classes directly but use them implicitly through series logging methods.

## Parent Module

See `../README.md` for information about Neptune types.

---
f7ae0475 2026-01-22T18:39:07
