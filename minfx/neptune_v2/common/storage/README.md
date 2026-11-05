# storage

File storage and streaming utilities for Neptune uploads and artifacts.

## Purpose

This module provides file storage and streaming utilities for Neptune
operations.
It handles efficient file uploads, chunking, and streaming for artifacts and
other file-based data.
[`FileChunker`] splits files into multipart upload chunks with size limits.
[`UploadEntry`] represents a source file or stream with a target path.
[`compress_to_tar_gz_in_memory`] builds tar.gz archives from upload entries
in memory.
Utility helpers manage upload packages, progress indicators, and file-name
normalization.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./datastream.py` - [`FileChunker`] chunking and in-memory tar.gz
  compression.
- `./storage_utils.py` - [`UploadEntry`], packages, and upload helpers.

## Usages

- The Neptune client uses this module for artifact, image, and attachment
  uploads.
- [`hosted_file_operations`] imports chunking and upload utilities for
  multipart backend uploads.
- [`normalize_file_name`] from storage utilities is used when packaging source
  code snapshots.
- See [`../README.md`] for the parent common utilities system overview.


[`FileChunker`]: datastream.py
[`UploadEntry`]: storage_utils.py
[`compress_to_tar_gz_in_memory`]: datastream.py
[`hosted_file_operations`]: ../../internal/backends/hosted_file_operations.py
[`normalize_file_name`]: storage_utils.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
