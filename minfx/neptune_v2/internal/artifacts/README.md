# artifacts

Internal artifact management for the Neptune client.

## Purpose

The artifacts module handles artifact tracking, hashing, and storage
coordination across different storage backends.
It defines core types and protocols used by [`FileHasher`] and artifact
drivers.
[`LocalFileHashStorage`] caches file hashes locally for performance.

## Subdirectories / Files

- `./drivers/` - Storage backend drivers for local and S3 artifact storage.
- `./__init__.py` - Package exports for [`LocalArtifactDriver`] and
  [`S3ArtifactDriver`].
- `./file_hasher.py` - [`FileHasher`] for artifact integrity verification.
- `./local_file_hash_storage.py` - [`LocalFileHashStorage`] for local hash
  caching.
- `./types.py` - Core artifact types, protocols, and metadata serialization.
- `./utils.py` - Artifact-related utility functions including [`sha1`] hashing.

## Usages

- Neptune uses this module internally to manage artifacts across storage
  backends.
- [`FileHasher`] computes and verifies file hashes during upload and download.
- [`LocalFileHashStorage`] avoids recomputing hashes for unchanged local
  files.
- Artifact drivers in `./drivers/` handle backend-specific storage
  operations.
- See [`../README.md`] for the parent internal module overview.


[`FileHasher`]: file_hasher.FileHasher
[`LocalFileHashStorage`]: local_file_hash_storage.LocalFileHashStorage
[`LocalArtifactDriver`]: drivers.LocalArtifactDriver
[`S3ArtifactDriver`]: drivers.S3ArtifactDriver
[`sha1`]: utils.sha1
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
