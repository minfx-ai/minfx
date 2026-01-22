# CLI

This module provides the Minfx command-line interface.

## Purpose

The CLI module implements command-line tools for managing Minfx data, including synchronization, status checking, and cleanup operations.

## Key Components

- `commands.py`: CLI command definitions (status, sync, clear)
- `status.py`: Status command implementation
- `sync.py`: Sync command implementation
- `clear.py`: Clear command implementation
- `containers.py`: Container management utilities
- `utils.py`: CLI utility functions (including multi-backend directory detection)

## Commands

- `minfx status`: List synchronized and unsynchronized objects
- `minfx sync`: Synchronize offline data with servers
- `minfx clear`: Remove synchronized data from local storage

## Multi-Backend Support

The CLI supports multi-backend directory structures where each backend has its own subdirectory named using DNS-based identifiers:
```
.neptune/async/run__<uuid>__<pid>__<key>/
    neptune2_localhost_8889/
    neptune2_localhost_8890/
```

The directory name is derived from the backend URL's DNS and port (e.g., `http://neptune2.localhost:8889` → `neptune2_localhost_8889`). This enables:
- Matching directories to backends via `NEPTUNE_API_TOKEN`
- Per-backend status and sync operations
- Human-readable directory names

The `is_multi_backend_directory()`, `get_backend_subdirs()`, and `get_backend_name_for_backend()` functions in `utils.py` handle this structure. Legacy `backend_N` format is also supported for backwards compatibility.

## Functionality

The CLI provides:
- Offline data synchronization
- Status reporting for local Minfx data
- Cleanup of synchronized data
- Path-based operation selection
- Multi-backend sync support

## Usage

Use the Minfx CLI from the command line:
```bash
minfx status  # Check sync status
minfx sync    # Sync offline data
minfx clear   # Clear synchronized data
```

## Parent Module

See `../README.md` for information about the Minfx client.

---
dedbdbb6 2026-01-20T21:10:47
