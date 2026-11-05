# api

This module provides the public API for fetching and querying Neptune data.

## Purpose

The api module implements the client-side API for fetching experiment data,
searching runs, and querying Neptune objects.
[`dtos.py`] defines data transfer objects for API responses such as
FileEntry.
[`searching_entries.py`] provides entry searching and filtering.
[`requests_utils.py`] supplies HTTP request utilities for API calls.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./dtos.py` - Data transfer objects for API responses including FileEntry.
- `./requests_utils.py` - HTTP request utilities for API calls.
- `./searching_entries.py` - Entry searching and filtering functionality.

## Usages

- Hosted backends import [`dtos.py`] and [`searching_entries.py`] for
  pagination and file metadata.
- [`requests_utils.py`] validates JSON responses from Swagger clients.
- High-level Neptune objects such as [`Run`] and [`Project`] use this module
  to fetch data from Neptune services.
- See [`../README.md`] for the parent neptune_v2 module overview.


[`dtos.py`]: dtos.py
[`searching_entries.py`]: searching_entries.py
[`requests_utils.py`]: requests_utils.py
[`Run`]: ../metadata_containers/run.py
[`Project`]: ../metadata_containers/project.py
[`../README.md`]: ../README.md

---
2026-08-27T14:54:08
