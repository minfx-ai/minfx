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

## Usage

These types are used internally to represent values logged to series attributes. Users typically don't interact with these classes directly but use them implicitly through series logging methods.

## Parent Module

See `../README.md` for information about Neptune types.

---
7dcfce5a 2026-01-18T14:43:38
