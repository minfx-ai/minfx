# types

Type definitions for Neptune values and attributes.

## Purpose

This module provides type definitions for Neptune values and attributes.
The types module defines the value types and type system used throughout
Neptune for representing different kinds of data.
[`Value`] is the abstract base class for all Neptune value types.
[`ValueVisitor`] implements the visitor pattern for type-safe operations.
[`ValueCopy`] supports copying values between attribute paths.
[`cast_value`] and [`cast_value_for_extend`] convert Python values into
Neptune value types.
[`Namespace`] represents nested attribute namespaces.
[`FileSet`] stores collections of files for upload.
[`Mode`] enumerates Neptune client connection modes.
[`ModelVersionStage`] enumerates model version lifecycle stages.
Subpackages [`atoms/`], [`series/`], and [`sets/`] define atomic, series,
and set value types.

## Subdirectories / Files

- `./atoms/` - Atomic value types such as [`Boolean`] and [`String`].
- `./series/` - Series value types such as [`FloatSeries`].
- `./sets/` - Set value types such as [`StringSet`].
- `./__init__.py` - Public exports for value types used by the client.
- `./file_set.py` - [`FileSet`] file collection value type.
- `./mode.py` - [`Mode`] Neptune client connection mode enumeration.
- `./model_version_stage.py` - [`ModelVersionStage`] model version stage
  enumeration.
- `./namespace.py` - [`Namespace`] nested attribute namespace value type.
- `./type_casting.py` - [`cast_value`] and [`cast_value_for_extend`] casting
  utilities.
- `./value.py` - [`Value`] abstract base class for Neptune values.
- `./value_copy.py` - [`ValueCopy`] value copying between attribute paths.
- `./value_visitor.py` - [`ValueVisitor`] visitor pattern for value types.

## Usages

- These types represent values stored in Neptune attributes internally.
- Users typically interact with them indirectly through attribute operations.
- Use [`cast_value`] when converting Python inputs into typed Neptune values.
- See [`../README.md`] for the parent Neptune v2 client overview.


[`Value`]: value.Value
[`ValueVisitor`]: value_visitor.ValueVisitor
[`ValueCopy`]: value_copy.ValueCopy
[`cast_value`]: type_casting.cast_value
[`cast_value_for_extend`]: type_casting.cast_value_for_extend
[`Namespace`]: namespace.Namespace
[`FileSet`]: file_set.FileSet
[`Mode`]: mode.Mode
[`ModelVersionStage`]: model_version_stage.ModelVersionStage
[`atoms/`]: atoms/README.md
[`series/`]: series/README.md
[`sets/`]: sets/README.md
[`Boolean`]: atoms/boolean.py
[`String`]: atoms/string.py
[`FloatSeries`]: series/float_series.py
[`StringSet`]: sets/string_set.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
