# sets

Set attribute types for Neptune experiments.

## Purpose

This module provides set attribute types for Neptune experiments.
Sets represent collections of unique values.
They are useful for tracking tags, labels, or any other collection of distinct
items.
[`Set`] is the base class for all set attributes.
[`StringSet`] stores unique string values with add, remove, assign, clear, and
fetch operations.
Set attributes maintain element uniqueness and enqueue backend operations for
synchronization.

## Subdirectories / Files

- `./__init__.py` - Public exports for [`StringSet`].
- `./set.py` - [`Set`] base class for set attributes.
- `./string_set.py` - [`StringSet`] for unique string value collections.

## Usages

- Sets are commonly used for tags and labels on Neptune runs.
- Add a tag with run["sys/tags"].add("production").
- Add multiple tags with run["sys/tags"].add(["experiment", "baseline"]).
- Remove a tag with run["sys/tags"].remove("baseline").
- Assign a list directly with run["sys/tags"] = ["lightning", "mnist"].
- See [`../README.md`] for the parent attributes module overview.


[`Set`]: set.Set
[`StringSet`]: string_set.StringSet
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
