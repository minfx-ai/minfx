# types

This module provides internal type definitions and utilities.

## Purpose

The internal types module defines common types, protocols, and type utilities
used throughout the Neptune codebase.
It provides file type detection, value stringification, and Neptune SDK
compatibility checks.
When users accidentally pass Neptune SDK types instead of minfx equivalents,
[`neptune_sdk_compat.py`] raises [`TypeError`] with migration guidance or
emits warnings for types that can auto-convert.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./file_types.py` - File type definitions and [`FileComposite`] handling.
- `./neptune_sdk_compat.py` - Neptune SDK type detection and compatibility
  checks.
- `./stringify_value.py` - Value stringification for logging via
  [`StringifyValue`].

## Usages

- Internal Neptune code imports [`file_types.py`] composites for local,
  in-memory, and stream file handling.
- [`stringify_value.py`] wraps values that need special logging treatment
  and exposes [`extract_if_stringify_value()`].
- [`neptune_sdk_compat.py`] detects accidental Neptune SDK types and raises
  [`TypeError`] with migration guidance.
- When users pass [`neptune.types.File`], use [`minfx.neptune_v2.types.File`]
  instead.
- When users pass [`neptune::StringifyValue`], use
  [`minfx.neptune_v2.utils.stringify_unsupported`] instead.
- When users pass [`neptune.Run`], use [`minfx.neptune_v2.Run`] instead.
- When users pass [`neptune.types.Namespace`], use
  [`minfx.neptune_v2.types.Namespace`] or a plain dict.
- When users pass [`neptune.types.Artifact`], use
  [`run['artifact'].track_files()`] instead.
- When users pass [`neptune.types atoms`], use plain Python primitives.
- When users pass [`neptune.types.StringSet`], use
  [`minfx.neptune_v2.types.StringSet`] or a plain set or list.
- When users pass [`neptune.types.FileSet`], use
  [`minfx.neptune_v2.types.FileSet`] or [`upload_files()`].
- When users pass [`neptune.types.FileSeries`], use
  [`minfx.neptune_v2.types.FileSeries`] instead.
- [`neptune.types.FloatSeries`] and [`neptune.types.StringSeries`] warn but
  auto-convert to minfx equivalents.
- See [`../README.md`] for the parent internal module overview.


[`FileComposite`]: file_types.FileComposite
[`StringifyValue`]: stringify_value.StringifyValue
[`extract_if_stringify_value()`]: stringify_value.extract_if_stringify_value
[`file_types.py`]: file_types.py
[`stringify_value.py`]: stringify_value.py
[`neptune_sdk_compat.py`]: neptune_sdk_compat.py
[`TypeError`]: https://docs.python.org/3/library/exceptions.html#TypeError
[`neptune.types.File`]: neptune_sdk_compat.check_not_neptune_sdk_file
[`minfx.neptune_v2.types.File`]: ../../types/atoms/file.py
[`neptune::StringifyValue`]: neptune_sdk_compat.py
[`minfx.neptune_v2.utils.stringify_unsupported`]: ../../utils.py
[`neptune.Run`]: neptune_sdk_compat.check_not_neptune_sdk_run
[`minfx.neptune_v2.Run`]: ../../metadata_containers/run.py
[`neptune.types.Namespace`]: neptune_sdk_compat.check_not_neptune_sdk_namespace
[`minfx.neptune_v2.types.Namespace`]: ../../types/namespace.py
[`neptune.types.Artifact`]: neptune_sdk_compat.check_not_neptune_sdk_artifact
[`run['artifact'].track_files()`]: ../../metadata_containers/run.py
[`neptune.types atoms`]: neptune_sdk_compat.py
[`neptune.types.StringSet`]: neptune_sdk_compat.check_not_neptune_sdk_string_set
[`minfx.neptune_v2.types.StringSet`]: ../../types/sets/string_set.py
[`neptune.types.FileSet`]: neptune_sdk_compat.check_not_neptune_sdk_file_set
[`minfx.neptune_v2.types.FileSet`]: ../../types/file_set.py
[`upload_files()`]: ../../handler.py
[`neptune.types.FileSeries`]: neptune_sdk_compat.py
[`minfx.neptune_v2.types.FileSeries`]: ../../types/series/file_series.py
[`neptune.types.FloatSeries`]: neptune_sdk_compat.warn_neptune_sdk_series
[`neptune.types.StringSeries`]: neptune_sdk_compat.warn_neptune_sdk_series
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
