# Internal Streams

This module provides stdout/stderr capture functionality.

## Purpose

The internal streams module captures stdout and stderr output from experiments and logs it to Neptune for later review.

## Key Components

- `std_stream_capture_logger.py`: Logger for captured stdout/stderr streams
- `std_capture_background_job.py`: Background job for stream capture

## Functionality

This module provides:
- Stdout/stderr capture during experiment execution
- Automatic logging of console output to Neptune
- Background stream monitoring
- Stream buffering and batching

## Usage

This module is used internally by the Neptune client to automatically capture and log console output when the capture feature is enabled.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
7dcfce5a 2026-01-18T14:43:38
