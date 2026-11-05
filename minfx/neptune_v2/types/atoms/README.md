# atoms

Value type classes for atomic Neptune attributes.

## Purpose

This module provides value type classes for atomic attributes.
The atom value types module defines data classes representing different
types of atomic values stored in Neptune attributes.
[`Atom`] is the base class for all atomic value types.
Typed atoms include [`Boolean`], [`Integer`], [`Float`], [`String`], and
[`Datetime`].
Reference atoms include [`File`], [`Artifact`], and [`GitRef`].
These value types provide type-safe value containers.
They support serialization and deserialization for backend storage.
They enable type checking and validation through the visitor pattern.

## Subdirectories / Files

- `./__init__.py` - Public exports for atom value types.
- `./artifact.py` - [`Artifact`] artifact reference value type.
- `./atom.py` - [`Atom`] base class for atomic value types.
- `./boolean.py` - [`Boolean`] boolean value type.
- `./datetime.py` - [`Datetime`] datetime value type.
- `./file.py` - [`File`] file value type.
- `./float.py` - [`Float`] floating-point value type.
- `./git_ref.py` - [`GitRef`] git reference value type.
- `./integer.py` - [`Integer`] integer value type.
- `./string.py` - [`String`] string value type.

## Usages

- These types represent values stored in atomic attributes internally.
- Users typically interact with them implicitly through attribute
  assignments rather than constructing them directly.
- See [`../README.md`] for the parent types module overview.


[`Atom`]: atom.Atom
[`Boolean`]: boolean.Boolean
[`Integer`]: integer.Integer
[`Float`]: float.Float
[`String`]: string.String
[`Datetime`]: datetime.Datetime
[`File`]: file.File
[`Artifact`]: artifact.Artifact
[`GitRef`]: git_ref.GitRef
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
