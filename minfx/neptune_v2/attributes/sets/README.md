# Set Attributes

This module provides set attribute types for Neptune experiments.

## Purpose

Sets represent collections of unique values, useful for tracking tags, labels, or any other collection of distinct items.

## Key Components

- `Set`: Base class for all set attributes
- `StringSet`: Set of unique string values

## Functionality

Set attributes support:
- Adding individual values or multiple values
- Removing values
- Checking membership
- Maintaining uniqueness of elements
- Efficient set operations

## Usage

Sets are commonly used for tags and labels:
```python
run["sys/tags"].add("production")
run["sys/tags"].add(["experiment", "baseline"])
run["sys/tags"].remove("baseline")
```

You can also assign lists, sets, or tuples directly:
```python
run["sys/tags"] = ["lightning", "mnist"]
```

## Parent Module

See `../README.md` for information about the attributes system.

---
9197f5d5 2026-01-21T23:52:40
