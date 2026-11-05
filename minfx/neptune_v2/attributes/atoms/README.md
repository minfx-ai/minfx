# atoms

Atomic (single-value) attribute types for Neptune experiments.

## Purpose

This module provides atomic (single-value) attribute types for Neptune
experiments.
Atoms represent single-value attributes that can be assigned and retrieved.
Unlike series, atoms hold a single value at a time rather than a sequence of
values.
[`Atom`] is the base class for all atomic attributes.
[`CopiableAtom`] extends [`Atom`] for atoms that support copying.
Typed atoms include [`Boolean`], [`Integer`], [`Float`], [`String`], and
[`Datetime`].
Reference atoms include [`File`], [`Artifact`], [`GitRef`], and
[`NotebookRef`].
[`ExperimentState`] tracks experiment run state.
Atom attributes support assignment, retrieval, type-specific validation, and
serialization for backend storage.
The [`Float`] attribute supports IEEE 754 special values including
[`float("nan")`], [`float("inf")`], and [`float("-inf")`].
These special values are encoded as strings during JSON serialization.

## Subdirectories / Files

- `./__init__.py` - Public exports for atom attribute types.
- `./artifact.py` - [`Artifact`] artifact reference attribute.
- `./atom.py` - [`Atom`] base class for atomic attributes.
- `./boolean.py` - [`Boolean`] boolean value attribute.
- `./copiable_atom.py` - [`CopiableAtom`] base for copyable atoms.
- `./datetime.py` - [`Datetime`] datetime value attribute.
- `./experiment_state.py` - [`ExperimentState`] experiment run state
  attribute.
- `./file.py` - [`File`] file attachment attribute.
- `./float.py` - [`Float`] floating-point attribute with IEEE 754 specials.
- `./git_ref.py` - [`GitRef`] git reference attribute.
- `./integer.py` - [`Integer`] integer value attribute.
- `./notebook_ref.py` - [`NotebookRef`] Jupyter notebook reference attribute.
- `./string.py` - [`String`] string value attribute.

## Usages

- Atoms store metadata and single-value parameters on Neptune runs.
- Assign a [`Float`] atom with run["parameters/learning_rate"] = 0.001.
- Assign a [`String`] atom with run["model/name"] = "ResNet50".
- Assign a [`Boolean`] atom with run["config/use_augmentation"] = True.
- See [`../README.md`] for the parent attributes module overview.


[`Atom`]: atom.Atom
[`Boolean`]: boolean.Boolean
[`Integer`]: integer.Integer
[`Float`]: float.Float
[`String`]: string.String
[`Datetime`]: datetime.Datetime
[`File`]: file.File
[`Artifact`]: artifact.Artifact
[`GitRef`]: git_ref.GitRef
[`NotebookRef`]: notebook_ref.NotebookRef
[`ExperimentState`]: experiment_state.ExperimentState
[`CopiableAtom`]: copiable_atom.CopiableAtom
[`float("nan")`]: float.py
[`float("inf")`]: float.py
[`float("-inf")`]: float.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
