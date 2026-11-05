# queue

Persistent disk-based queue functionality for reliable operation storage and
synchronization.

## Purpose

The queue components implement a durable, disk-backed queue system.
Operations are not lost even if the process crashes or is interrupted.
[`DiskQueue`] provides thread-safe persistence with log rotation and sync
tracking.
[`InMemoryQueue`] offers an in-memory alternative for benchmarking without
disk overhead.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./disk_queue.py` - [`DiskQueue`] and [`InMemoryQueue`] implementations.
- `./json_file_splitter.py` - [`JsonFileSplitter`] for streaming JSON log
  reads.
- `./log_file.py` - [`LogFile`] append-only log persistence.
- `./sync_offset_file.py` - [`SyncOffsetFile`] sync progress tracking.

## Usages

- The Neptune client queues operations through [`DiskQueue`] for reliable
  transmission to the backend.
- Set NEPTUNE_IN_MEMORY_QUEUE=1 to benchmark with [`InMemoryQueue`] instead
  of disk persistence.
  Data is lost if the process crashes while using [`InMemoryQueue`].
- See the parent [`../README.md`] for the broader core components layout.


[`DiskQueue`]: disk_queue.DiskQueue
[`InMemoryQueue`]: disk_queue.InMemoryQueue
[`LogFile`]: log_file.LogFile
[`JsonFileSplitter`]: json_file_splitter.JsonFileSplitter
[`SyncOffsetFile`]: sync_offset_file.SyncOffsetFile
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
