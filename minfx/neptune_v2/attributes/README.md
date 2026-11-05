# attributes

This module provides the attribute system for Neptune experiments.

## Purpose

The attributes module implements the core attribute types (atoms, series, sets)
that represent different kinds of data logged to Neptune.
[`Attribute`] is the base class for all attribute implementations.
[`Namespace`] organizes attributes hierarchically with dictionary-style
access.
[`FileSet`] handles directory uploads as a single attribute.
The module supports hierarchical namespace organization (e.g.,
[`run["metrics/loss"]`]).
It provides multiple attribute types (atoms, series, sets).
It enables type-safe attribute access and lazy attribute creation.
It queues operations for backend synchronization.

## Subdirectories / Files

- `./atoms/` - Atomic (single-value) attributes.
- `./series/` - Time-series attributes.
- `./sets/` - Set attributes.
- `./__init__.py` - Public exports for attribute types.
- `./attribute.py` - [`Attribute`] base attribute class.
- `./constants.py` - Attribute path and namespace constants.
- `./file_set.py` - [`FileSet`] file set attribute implementation.
- `./namespace.py` - [`Namespace`] for organizing attributes
  hierarchically.
- `./utils.py` - Utility functions including [`create_attribute_from_type`].

## Usages

- Users interact with attributes through dictionary-style access on Neptune
  objects.
- Assign an atom with run["parameters/learning_rate"] = 0.001.
- Append to a series with run["metrics/loss"].append(0.5).
- Add to a set with run["sys/tags"].add("experiment").
- See [`../README.md`] for the parent neptune_v2 module overview.


[`Attribute`]: attribute.Attribute
[`Namespace`]: namespace.Namespace
[`FileSet`]: file_set.FileSet
[`create_attribute_from_type`]: utils.create_attribute_from_type
[`run["metrics/loss"]`]: namespace.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
