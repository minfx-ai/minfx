# components

Fundamental components for Neptune's operation system.

## Purpose

The components module implements core abstractions and implementations for
operation storage, metadata management, and queue systems.
[`Resource`] and [`WithResources`] in [`abstract.py`] provide lifecycle
management for persistent components.
[`OperationStorage`] manages on-disk upload paths for operations.
[`MetadataFile`] persists JSON metadata across process restarts.
The [`queue/`] submodule provides disk-backed queuing for reliable operation
handling.

## Subdirectories / Files

- `./queue/` - Disk-based persistent queue implementation.
- `./__init__.py` - Package marker with no public re-exports.
- `./abstract.py` - [`Resource`], [`WithResources`], and [`AutoCloseable`]
  base classes.
- `./metadata_file.py` - [`MetadataFile`] JSON metadata persistence.
- `./operation_storage.py` - [`OperationStorage`] on-disk operation storage.

## Usages

- Operation processors compose [`OperationStorage`], [`MetadataFile`], and
  [`DiskQueue`] from [`queue/`] for offline and async processing.
- [`Resource`] subclasses manage cleanup, flush, and close lifecycle hooks.
- See [`../README.md`] for the parent core module overview.


[`Resource`]: abstract.Resource
[`WithResources`]: abstract.WithResources
[`AutoCloseable`]: abstract.AutoCloseable
[`OperationStorage`]: operation_storage.OperationStorage
[`MetadataFile`]: metadata_file.MetadataFile
[`abstract.py`]: abstract.py
[`queue/`]: queue/
[`DiskQueue`]: queue/disk_queue.DiskQueue
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
