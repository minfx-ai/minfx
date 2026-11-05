# backends

Common data models and utilities for backend communication.

## Purpose

The backends module defines shared data structures and utilities used across
different backend implementations for communicating with Neptune services.
[`api_model.py`] holds common API data models such as [`MultipartConfig`] for
file uploads.
[`utils.py`] provides shared utility functions for backend operations.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./api_model.py` - [`MultipartConfig`] defaults for multipart uploads.
- `./utils.py` - Retry helpers and API exception wrapping utilities.

## Usages

- [`hosted_client.py`] wraps HTTP calls with [`with_api_exceptions_handler`].
- [`hosted_file_operations.py`] uses [`MultipartConfig`] for chunked uploads.
- [`datastream.py`] reads [`MultipartConfig`] chunk size limits.
- [`cli/containers.py`] formats rate-limit warnings via
  [`format_rate_limit_warning`].
- See [`../README.md`] for the parent common utilities overview.


[`MultipartConfig`]: api_model.MultipartConfig
[`with_api_exceptions_handler`]: utils.with_api_exceptions_handler
[`format_rate_limit_warning`]: utils.format_rate_limit_warning
[`hosted_client.py`]: ../../internal/backends/hosted_client.py
[`hosted_file_operations.py`]: ../../internal/backends/hosted_file_operations.py
[`cli/containers.py`]: ../../cli/containers.py
[`datastream.py`]: ../storage/datastream.py
[`api_model.py`]: api_model.py
[`utils.py`]: utils.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
