# sets

Set value types for Neptune attributes.

## Purpose

This module defines value type classes for set attributes in Neptune.
Sets represent collections of unique values stored in attributes.
[`Set`] is the abstract base class extending [`Value`] with the visitor
pattern.
[`StringSet`] stores unique string values and implements set operations for
backend serialization.

## Subdirectories / Files

- `./__init__.py` - Public exports for [`StringSet`].
- `./set.py` - [`Set`] base class for all set value types.
- `./string_set.py` - [`StringSet`] for unique string value collections.

## Usages

- Internal Neptune code uses these types to represent set attribute values.
- [`StringSet`] accepts an iterable of strings and deduplicates them on init.
- The visitor pattern in [`Set::accept()`] dispatches type-specific handling.
- Users typically interact with sets through attribute APIs rather than these
  classes directly.
- See [`../README.md`] for the parent types module overview.


[`Set`]: set.Set
[`StringSet`]: string_set.StringSet
[`Value`]: ../value.py
[`Set::accept()`]: set.Set.accept
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
