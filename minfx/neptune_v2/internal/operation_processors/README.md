# Internal Operation Processors

This module provides operation processing implementations for different execution modes.

## Purpose

The operation processors module handles the execution and transmission of operations (logging, uploads, etc.) to Neptune backends in various modes (async, sync, offline, read-only).

## Key Components

- `operation_processor.py`: Abstract base class for operation processors
- `async_operation_processor.py`: Asynchronous operation processing with background threads
- `sync_operation_processor.py`: Synchronous operation processing (blocking)
- `offline_operation_processor.py`: Offline operation processing (no network)
- `read_only_operation_processor.py`: Read-only mode (no operations allowed)
- `multi_backend_operation_processor.py`: Multi-backend operation processing
- `factory.py`: Factory for creating operation processor instances
- `operation_logger.py`: Operation logging utilities

## Functionality

This module provides:
- Multiple operation processing modes
- Background operation execution
- Operation queuing and batching
- Error handling and retry logic
- Synchronization control (pause, resume, flush)

## Usage

This module is used internally by the Neptune client to process operations based on the selected mode (async by default). Users control the mode through initialization parameters.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
932aeafe 2026-01-22T01:15:37
