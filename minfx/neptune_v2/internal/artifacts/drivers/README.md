# Artifact Drivers

This module provides storage backend drivers for artifact management.

## Purpose

Artifact drivers abstract the storage layer for artifacts, enabling Neptune to work with different storage backends (local filesystem, S3, etc.) through a common interface.

## Key Components

- `local.py`: Local filesystem artifact driver for storing artifacts on disk
- `s3.py`: Amazon S3 artifact driver for cloud-based artifact storage

## Functionality

Each driver implements:
- Artifact file upload and download
- Metadata extraction (size, modification time, hash)
- Path matching and validation
- Storage-specific optimizations

## Usage

Drivers are automatically selected based on the artifact path scheme:
- `file://` or local paths use the local driver
- `s3://` paths use the S3 driver

This abstraction allows users to track artifacts regardless of where they are stored.

## Parent Module

See `../README.md` for information about the artifacts system.

---
7dcfce5a 2026-01-18T14:43:38
