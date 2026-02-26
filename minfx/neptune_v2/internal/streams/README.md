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
- Line buffering for clean log entries

## Line Buffering

The capture uses line buffering to ensure each log entry contains a complete line.
Without buffering, Python's `print()` function would create separate entries:

```
print("hello")  # Internally calls: write("hello"), write("\n")
```

This would result in fragmented entries: `"hello"`, `"\n"`.

With line buffering, partial writes are accumulated until a newline is received,
producing a single entry: `"hello\n"`.

**Behavior:**
- Complete lines (ending with `\n`) are logged as single entries
- Multiple lines in one write produce multiple entries
- Partial lines (no newline) are buffered until newline or `close()`
- On `close()`, any remaining buffered content is flushed

## Usage

This module is used internally by the Neptune client to automatically capture and log console output when the capture feature is enabled.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
66b9539e 2026-01-25T15:43:12
