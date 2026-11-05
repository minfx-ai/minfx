# init

This module provides initialization logic for Neptune runs and projects.

## Purpose

The internal init module supplies default values and thresholds for Neptune
run and project initialization.
[`parameters.py`] centralizes flush periods, stop timeouts, async lag limits,
and offline project placeholders.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./parameters.py` - Default initialization constants and thresholds.

## Usages

- Metadata containers import from [`parameters.py`] when users call
  [`neptune.init_run()`] or [`neptune.init_project()`].
- Async operation processors and signal handlers reuse timing thresholds
  defined in [`parameters.py`].
- See [`../README.md`] for the parent internal module overview.


[`parameters.py`]: parameters.py
[`neptune.init_run()`]: ../../__init__.py
[`neptune.init_project()`]: ../../__init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
