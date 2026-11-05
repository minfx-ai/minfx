# operation_processors

Operation processing implementations for different Neptune execution modes.

## Purpose

The operation processors module handles the execution and transmission of
operations (logging, uploads, etc.) to Neptune backends in various modes
(async, sync, offline, read-only).
[`OperationProcessor`] is the abstract base for all processor implementations.
[`get_operation_processor`] selects the concrete processor from client
initialization parameters.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./async_operation_processor.py` - [`AsyncOperationProcessor`] for background
  thread operation processing.
- `./factory.py` - [`get_operation_processor`] factory and async builder.
- `./lazy_operation_processor_wrapper.py` - [`LazyOperationProcessorWrapper`]
  for deferred processor initialization.
- `./multi_backend_operation_processor.py` - [`MultiBackendOperationProcessor`]
  for multi-backend operation routing.
- `./offline_operation_processor.py` - [`OfflineOperationProcessor`] for
  offline operation persistence without network.
- `./operation_logger.py` - [`ProcessorStopLogger`] and sync status signals.
- `./operation_processor.py` - [`OperationProcessor`] abstract base class.
- `./read_only_operation_processor.py` - [`ReadOnlyOperationProcessor`] that
  rejects mutating operations.
- `./sync_operation_processor.py` - [`SyncOperationProcessor`] for blocking
  synchronous operation processing.
- `./upload_tracker.py` - [`UploadTracker`] for tracking artifact upload
  progress.
- `./utils.py` - Container path and metadata helpers for operation processors.

## Usages

- The Neptune client obtains a processor through [`get_operation_processor`]
  during initialization.
- Async mode uses [`AsyncOperationProcessor`] with background threads for
  non-blocking operation submission.
- Sync mode uses [`SyncOperationProcessor`] to block until each operation
  completes.
- Offline mode uses [`OfflineOperationProcessor`] to persist operations
  locally without network access.
- Read-only mode uses [`ReadOnlyOperationProcessor`] to prevent mutating
  operations.
- Multi-backend setups route operations through
  [`MultiBackendOperationProcessor`].
- See [`../README.md`] for the parent internal module overview.


[`OperationProcessor`]: operation_processor.OperationProcessor
[`AsyncOperationProcessor`]: async_operation_processor.AsyncOperationProcessor
[`SyncOperationProcessor`]: sync_operation_processor.SyncOperationProcessor
[`OfflineOperationProcessor`]: offline_operation_processor.py
[`ReadOnlyOperationProcessor`]: read_only_operation_processor.py
[`MultiBackendOperationProcessor`]: multi_backend_operation_processor.py
[`LazyOperationProcessorWrapper`]: lazy_operation_processor_wrapper.py
[`get_operation_processor`]: factory.get_operation_processor
[`ProcessorStopLogger`]: operation_logger.ProcessorStopLogger
[`UploadTracker`]: upload_tracker.UploadTracker
[`../README.md`]: ../README.md

---
2026-09-23T15:47:53
