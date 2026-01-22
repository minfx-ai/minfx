# Core Components

This module provides fundamental components for Neptune's operation system.

## Purpose

The components module implements core abstractions and implementations for operation storage, metadata management, and queue systems.

## Key Components

- `abstract.py`: Abstract base classes for components (Resource, WithResources)
- `operation_storage.py`: Storage system for operations
- `metadata_file.py`: Metadata file handling

## Submodules

- `queue/`: Disk-based persistent queue implementation

## Functionality

This module provides:
- Resource lifecycle management (start, stop, cleanup)
- Operation storage and retrieval
- Metadata persistence
- Queue system for reliable operation handling

## Usage

This module is used internally by Neptune to manage the lifecycle of operations and ensure data persistence across process restarts.

## Parent Module

See `../README.md` for information about the core module.

---
dedbdbb6 2026-01-20T21:10:47
