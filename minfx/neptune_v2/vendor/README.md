# Vendor

This module contains vendored third-party libraries.

## Purpose

The vendor module includes copies of third-party libraries that are bundled with Neptune to avoid external dependencies or to use modified versions.

## Key Components

- `pynvml.py`: Python bindings for NVIDIA Management Library (NVML) for GPU monitoring
- `lib_programname.py`: Program name detection utilities

## Functionality

This module provides:
- NVIDIA GPU monitoring without requiring separate pynvml installation
- Program name detection for various environments
- Self-contained third-party functionality

## Usage

These vendored libraries are used internally by Neptune components (e.g., GPU monitoring) and are not intended for direct use by users.

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
7dcfce5a 2026-01-18T14:43:38
