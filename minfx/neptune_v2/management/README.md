# management

This module provides the management API for Neptune workspaces and projects.

## Purpose

The management module implements administrative operations for managing Neptune
workspaces, projects, and related resources.
[`exceptions.py`] defines management-specific failure types.
The [`internal/`] submodule implements the HTTP-backed management API.

## Subdirectories / Files

- `./internal/` - Internal management API implementation.
- `./__init__.py` - Public management API re-exports and usage examples.
- `./exceptions.py` - Management-specific exception types.

## Usages

- Import the public API from minfx.neptune_v2.management.
- Use [`__init__.py`] exports for workspace and project administration.
- [`exceptions.py`] raises typed failures when management operations fail.
- See [`../README.md`] for the parent neptune_v2 module overview.


[`__init__.py`]: __init__.py
[`exceptions.py`]: exceptions.py
[`internal/`]: internal/
[`../README.md`]: ../README.md

---
2026-08-27T14:54:08
