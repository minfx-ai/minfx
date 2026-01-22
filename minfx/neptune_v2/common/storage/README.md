# Storage

This module provides file storage and streaming utilities for Neptune operations.

## Purpose

The storage module handles efficient file uploads, chunking, and streaming for artifacts and other file-based data.

## Key Components

- `datastream.py`: File chunking and streaming for efficient uploads
- `storage_utils.py`: Utility functions for storage operations

## Functionality

This module provides:
- File chunking for multipart uploads
- Streaming data handling
- Upload entry management
- Efficient file transfer utilities

## Usage

This module is used internally by the Neptune client to handle file uploads, including artifacts, images, and other file attachments, with support for large files through chunking and streaming.

## Parent Module

See `../README.md` for information about the common utilities system.

---
7dcfce5a 2026-01-18T14:43:38
