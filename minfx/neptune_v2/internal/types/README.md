# Internal Types

This module provides internal type definitions and utilities.

## Purpose

The internal types module defines common types, protocols, and type utilities used throughout the Neptune codebase.

## Key Components

- `file_types.py`: File type definitions and detection
- `stringify_value.py`: Value stringification for logging
- `neptune_sdk_compat.py`: Neptune SDK type detection and compatibility checks

## Functionality

This module provides:
- File type detection and handling
- Value stringification for various types
- Type checking and validation utilities
- Neptune SDK compatibility detection (raises helpful TypeError when Neptune SDK types are used instead of minfx equivalents)

## Neptune SDK Compatibility

When users accidentally use Neptune SDK types instead of minfx equivalents, the compatibility module detects this and raises a `TypeError` with a helpful message explaining which minfx import to use (or emits a warning for types that can be auto-converted).

### Types that raise TypeError:
- `neptune.types.File` → use `minfx.neptune_v2.types.File`
- `neptune.internal.types.stringify_value.StringifyValue` → use `minfx.neptune_v2.utils.stringify_unsupported`
- `neptune.Run` → use `minfx.neptune_v2.Run`
- `neptune.types.Namespace` → use `minfx.neptune_v2.types.Namespace` or plain dict
- `neptune.types.Artifact` → use `run['artifact'].track_files()`
- `neptune.types.Boolean/Integer/Float/String/Datetime` → use plain Python primitives
- `neptune.types.StringSet` → use `minfx.neptune_v2.types.StringSet` or plain set/list
- `neptune.types.FileSet` → use `minfx.neptune_v2.types.FileSet` or `upload_files()`
- `neptune.types.FileSeries` → use `minfx.neptune_v2.types.FileSeries`

### Types that warn but auto-convert:
- `neptune.types.FloatSeries` → warns, converts to `minfx.neptune_v2.types.FloatSeries`
- `neptune.types.StringSeries` → warns, converts to `minfx.neptune_v2.types.StringSeries`

## Usage

This module is used internally throughout the Neptune codebase to provide consistent type handling and validation.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
4ff6e696 2026-01-22T18:58:51
