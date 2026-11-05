# core

Core components for Neptune's operation system.

## Purpose

The core module implements fundamental components for operation storage,
queuing, and metadata management.
The [`components/`] submodule provides abstractions, on-disk storage, metadata
persistence, and a disk-backed queue.
[`components/abstract.py`] defines base classes for resource lifecycle
management.
[`components/operation_storage.py`] implements operation storage and retrieval.
[`components/metadata_file.py`] handles metadata file management.
[`components/queue/`] provides a persistent queue implementation.

## Subdirectories / Files

- `./components/` - Abstractions, storage, metadata, and queue implementations.
- `./__init__.py` - Package marker with no public re-exports.

## Usages

- Neptune uses this module internally to manage operations and ensure data
  persistence.
- Operation processors compose storage, metadata, and queue components from
  [`components/`].
- See [`../README.md`] for information about the Neptune v2 client.


[`components/`]: components/
[`components/abstract.py`]: components/abstract.py
[`components/operation_storage.py`]: components/operation_storage.py
[`components/metadata_file.py`]: components/metadata_file.py
[`components/queue/`]: components/queue/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
