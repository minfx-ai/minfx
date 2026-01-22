# Atom Attributes

This module provides atomic (single-value) attribute types for Neptune experiments.

## Purpose

Atoms represent single-value attributes that can be assigned and retrieved. Unlike series, atoms hold a single value at a time rather than a sequence of values.

## Key Components

- `Atom`: Base class for all atomic attributes
- `Boolean`: Boolean value attribute
- `Integer`: Integer value attribute
- `Float`: Floating-point value attribute
- `String`: String value attribute
- `Datetime`: Datetime value attribute
- `File`: File attachment attribute
- `Artifact`: Artifact reference attribute
- `GitRef`: Git reference attribute
- `NotebookRef`: Jupyter notebook reference attribute
- `RunState`: Experiment run state attribute
- `CopiableAtom`: Base class for atoms that support copying

## Functionality

Atom attributes support:
- Assignment of single values
- Retrieval of current value
- Type-specific validation
- Serialization for backend storage

## Usage

Atoms are used to store metadata and single-value parameters:
```python
run["parameters/learning_rate"] = 0.001  # Float atom
run["model/name"] = "ResNet50"  # String atom
run["config/use_augmentation"] = True  # Boolean atom
```

## Parent Module

See `../README.md` for information about the attributes system.

---
7dcfce5a 2026-01-18T14:43:38
