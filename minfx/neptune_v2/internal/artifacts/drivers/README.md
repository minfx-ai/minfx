# drivers

Storage backend drivers for artifact management in Neptune.

## Purpose

Artifact drivers abstract the storage layer for artifacts.
Neptune uses them to work with different storage backends through a common
interface.
[`LocalArtifactDriver`] stores artifacts on the local filesystem.
[`S3ArtifactDriver`] stores artifacts in Amazon S3.

## Subdirectories / Files

- `./__init__.py` - Package exports for [`LocalArtifactDriver`] and
  [`S3ArtifactDriver`].
- `./local.py` - [`LocalArtifactDriver`] for local filesystem artifact
  storage.
- `./s3.py` - [`S3ArtifactDriver`] for Amazon S3 artifact storage.

## Usages

- Neptune selects a driver from the artifact path scheme.
- [`file://`] or local paths use [`LocalArtifactDriver`].
- [`s3://`] paths use [`S3ArtifactDriver`].
- Each driver handles upload, download, metadata extraction, and path
  validation for its backend.
- See [`../README.md`] for the parent artifacts module overview.


[`LocalArtifactDriver`]: local.LocalArtifactDriver
[`S3ArtifactDriver`]: s3.S3ArtifactDriver
[`file://`]: local.py
[`s3://`]: s3.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
