# Internal Artifacts

This module provides internal artifact management functionality.

## Purpose

The internal artifacts module handles artifact tracking, hashing, and storage coordination across different storage backends.

## Key Components

- `types.py`: Core artifact types and interfaces (ArtifactDriver, ArtifactFileData, ArtifactFileType)
- `file_hasher.py`: File hashing utilities for artifact integrity verification
- `local_file_hash_storage.py`: Local storage for artifact hash caching
- `utils.py`: Artifact-related utility functions

## Submodules

- `drivers/`: Storage backend drivers (local, S3)

## Functionality

This module provides:
- Artifact type definitions and protocols
- File hashing for integrity verification
- Hash caching for performance
- Driver abstraction for different storage backends
- Artifact metadata serialization

## Usage

This module is used internally by the Neptune client to manage artifacts across different storage backends, ensuring data integrity and efficient storage operations.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
7dcfce5a 2026-01-18T14:43:38
