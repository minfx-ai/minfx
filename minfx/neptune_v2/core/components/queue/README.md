# Queue Components

This module provides persistent disk-based queue functionality for reliable operation storage and synchronization.

## Purpose

The queue components implement a durable, disk-backed queue system that ensures operations are not lost even if the process crashes or is interrupted.

## Key Components

- `DiskQueue`: Thread-safe disk-backed queue for storing and retrieving operations
- `InMemoryQueue`: In-memory queue for benchmarking (no disk persistence)
- `LogFile`: Manages append-only log files for queue persistence
- `JsonFileSplitter`: Splits large JSON log files for efficient processing
- `SyncOffsetFile`: Tracks synchronization progress across queue files

## Functionality

The queue system:
- Persists operations to disk for durability
- Supports concurrent access with thread safety
- Tracks which operations have been synchronized
- Handles log file rotation and cleanup
- Provides batch processing capabilities

## Usage

This module is used by the Neptune client to queue operations (logging metrics, uploading files, etc.) for reliable transmission to the backend, ensuring no data is lost even if network connectivity is interrupted.

### Benchmarking with In-Memory Queue

For benchmarking to measure the overhead of disk persistence, you can enable the in-memory queue:

```bash
export NEPTUNE_IN_MEMORY_QUEUE=1
python your_benchmark.py
```

**WARNING**: When using `InMemoryQueue`, data will be lost if the process crashes.

## Parent Module

See `../../README.md` for information about the core components system.

---
dedbdbb6 2026-01-20T21:10:47
