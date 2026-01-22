# Internal Utils

This module provides internal utility functions used throughout Neptune.

## Purpose

The internal utils module contains a wide variety of utility functions for common tasks like logging, path handling, image processing, git integration, and more.

## Key Components

- `backend_name.py`: Backend name utilities for multi-backend URL-to-directory mapping
- `logger.py`: Logging utilities with terminal color support
- `paths.py`: Path handling utilities
- `images.py`: Image processing utilities
- `git.py`: Git repository integration
- `source_code.py`: Source code tracking
- `hashing.py`: Hashing utilities
- `iteration.py`: Iteration and batching utilities
- `iso_dates.py`: ISO date/time handling
- `deprecation.py`: Deprecation warning utilities
- `requirement_check.py`: Dependency checking
- `dependency_tracking.py`: Dependency version tracking
- `ping_background_job.py`: Background ping job
- `uncaught_exception_handler.py`: Exception handling
- `process_killer.py`: Process termination utilities
- `disk_utilization.py`: Disk usage monitoring
- `s3.py`: S3 utilities
- `limits.py`: Limit constants
- `run_state.py`: Run state management
- `runningmode.py`: Running mode detection

## Functionality

This module provides a wide range of utilities for:
- Logging and debugging with colored terminal output
- File and path operations
- Image processing and conversion
- Git integration and source code tracking
- Dependency management
- Background jobs
- Exception handling
- Resource monitoring

## Logging Colors

The logger module provides colored terminal output for better readability:

| Log Level | Color |
|-----------|-------|
| DEBUG | Bright Blue |
| INFO | Bright Green |
| WARNING | Bright Yellow |
| ERROR | Bright Red |
| CRITICAL | Bold Bright Red |

Additionally:
- Timestamps are displayed in dim cyan
- Logger names are displayed in dim magenta

### Color Control

Colors are automatically enabled when outputting to a terminal (TTY). You can control color output with environment variables:

| Variable | Effect |
|----------|--------|
| `MINFX_LOG_COLOR=1` | Force colors on |
| `MINFX_LOG_COLOR=0` | Force colors off |
| `NO_COLOR` | Disable colors (standard, https://no-color.org/) |

## Usage

This module is used internally throughout the Neptune codebase to provide common functionality and avoid code duplication.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
456a7279 2026-01-22T00:27:31
