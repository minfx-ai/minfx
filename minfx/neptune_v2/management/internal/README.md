# internal

Internal management API functionality for Neptune workspaces and projects.

## Purpose

The management internal module implements the internal API for Neptune
management operations.
It covers project administration, workspace management, and related
administrative tasks.
[`api.py`] exposes the core management functions.
[`dto.py`], [`types.py`], and [`utils.py`] provide supporting data types and
helpers.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./api.py` - Internal management API for projects, workspaces, and trash.
- `./dto.py` - Data transfer objects for management API requests and responses.
- `./types.py` - Role and visibility type definitions for management.
- `./utils.py` - Project and workspace name parsing and validation helpers.

## Usages

- The public management API delegates administrative operations to this
  module.
- [`api.py`] implements create, delete, member, and service-account
  operations for projects and workspaces.
- See [`../../README.md`] for the parent management module overview.


[`api.py`]: api.py
[`dto.py`]: dto.py
[`types.py`]: types.py
[`utils.py`]: utils.py
[`../../README.md`]: ../../README.md

---
2026-08-27T14:54:08
