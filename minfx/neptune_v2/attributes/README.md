# Attributes

This module provides the attribute system for Neptune experiments.

## Purpose

The attributes module implements the core attribute types (atoms, series, sets) that represent different kinds of data logged to Neptune.

## Key Components

- `attribute.py`: Base attribute class
- `namespace.py`: Namespace for organizing attributes hierarchically
- `file_set.py`: File set attribute implementation
- `constants.py`: Attribute-related constants
- `utils.py`: Attribute utility functions

## Submodules

- `atoms/`: Atomic (single-value) attributes
- `series/`: Time-series attributes
- `sets/`: Set attributes

## Functionality

The attributes system provides:
- Hierarchical namespace organization (e.g., `run["metrics/loss"]`)
- Multiple attribute types (atoms, series, sets)
- Type-safe attribute access
- Lazy attribute creation
- Operation queuing for backend synchronization

## Usage

Users interact with attributes through dictionary-style access on Neptune objects:
```python
run["parameters/learning_rate"] = 0.001  # Atom
run["metrics/loss"].append(0.5)  # Series
run["sys/tags"].add("experiment")  # Set
```

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
9197f5d5 2026-01-21T23:52:40
