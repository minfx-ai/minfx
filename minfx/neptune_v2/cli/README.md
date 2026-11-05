# cli

This module provides the Minfx command-line interface.

## Purpose

The CLI module implements command-line tools for managing Minfx data.
It covers synchronization, status checking, and cleanup operations.
[`commands.py`] defines the Click commands for status, sync, and clear.
[`status.py`], [`sync.py`], and [`clear.py`] implement each command runner.
[`containers.py`] models async, offline, and execution directories.
[`utils.py`] provides multi-backend directory detection and metadata
lookup helpers.
Multi-backend layouts use DNS-based subdirectory names such as
[`neptune2_localhost_8889`], derived from backend URLs like
[`http://neptune2.localhost:8889`].
[`is_multi_backend_directory()`], [`get_backend_subdirs()`], and
[`get_backend_name_for_backend()`] in [`utils.py`] resolve those layouts.
Legacy [`backend_N`] directory names remain supported.

## Subdirectories / Files

- `./__init__.py` - Public exports for status and sync commands.
- `./__main__.py` - Click entry point registering the minfx command group.
- `./clear.py` - Clear command runner for removing synchronized data.
- `./collect.py` - Collects async and offline containers from data paths.
- `./commands.py` - Click command definitions for status, sync, and clear.
- `./containers.py` - Async, offline, and execution container abstractions.
- `./path_option.py` - Shared Click path option for Neptune data directories.
- `./status.py` - Status command runner listing sync state.
- `./sync.py` - Sync command runner uploading offline data.
- `./utils.py` - Multi-backend detection and metadata lookup helpers.

## Usages

- Run [`minfx status`] to list synchronized and unsynchronized objects in a
  Neptune data directory.
- Run [`minfx sync`] to upload offline data to configured backends.
- Run [`minfx clear`] to remove synchronized data from local storage.
- Set [`NEPTUNE_API_TOKEN`] so the CLI can match subdirectories to backends
  during status and sync operations.
- See [`../README.md`] for the parent Neptune v2 client overview.


[`commands.py`]: commands.py
[`status.py`]: status.py
[`sync.py`]: sync.py
[`clear.py`]: clear.py
[`containers.py`]: containers.py
[`utils.py`]: utils.py
[`minfx status`]: commands.py
[`minfx sync`]: commands.py
[`minfx clear`]: commands.py
[`http://neptune2.localhost:8889`]: utils.py
[`neptune2_localhost_8889`]: utils.py
[`NEPTUNE_API_TOKEN`]: utils.py
[`get_backend_subdirs()`]: utils.get_backend_subdirs
[`is_multi_backend_directory()`]: utils.is_multi_backend_directory
[`get_backend_name_for_backend()`]: utils.get_backend_name_for_backend
[`backend_N`]: utils.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
