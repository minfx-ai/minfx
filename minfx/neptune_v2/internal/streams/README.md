# streams

Stdout and stderr capture for Neptune experiment logging.

## Purpose

The internal streams module captures stdout and stderr output from experiments
and logs it to Neptune for later review.
[`StdStreamCaptureLogger`] wraps a stream with line buffering so each log
entry contains a complete line.
[`StdoutCaptureBackgroundJob`] and [`StderrCaptureBackgroundJob`] manage
capture lifecycle as background jobs during a run.

The capture uses line buffering to avoid fragmented log entries.
Without buffering, Python's [`print()`] would emit separate entries for each
partial write:

```
print("hello")  # Internally calls: write("hello"), write("\n")
```

That produces fragmented entries such as [`"hello"`] and [`"\n"`].
With buffering, partial writes accumulate until a newline arrives.
The result is a single entry such as [`"hello\n"`].
Complete lines ending with [`\n`] are logged as one entry.
Multiple lines in one write produce multiple entries.
Partial lines without a newline wait until newline or [`close()`].
On [`close()`], remaining buffered content is flushed.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./std_capture_background_job.py` - [`StdoutCaptureBackgroundJob`] and
  [`StderrCaptureBackgroundJob`] for run lifecycle capture.
- `./std_stream_capture_logger.py` - [`StdStreamCaptureLogger`],
  [`StdoutCaptureLogger`], and [`StderrCaptureLogger`] implementations.

## Usages

- [`metadata_containers/run.py`] appends capture jobs when stdout or stderr
  capture is enabled on a run.
- [`StdoutCaptureBackgroundJob`] starts [`StdoutCaptureLogger`] on start and
  calls [`close()`] on stop.
- [`StderrCaptureBackgroundJob`] starts [`StderrCaptureLogger`] on start and
  calls [`close()`] on stop.
- See [`../README.md`] for the parent internal module overview.


[`StdStreamCaptureLogger`]: std_stream_capture_logger.StdStreamCaptureLogger
[`StdoutCaptureLogger`]: std_stream_capture_logger.StdoutCaptureLogger
[`StderrCaptureLogger`]: std_stream_capture_logger.StderrCaptureLogger
[`StdoutCaptureBackgroundJob`]: std_capture_background_job.py
[`StderrCaptureBackgroundJob`]: std_capture_background_job.py
[`print()`]: std_stream_capture_logger.py
[`"hello"`]: std_stream_capture_logger.py
[`"\n"`]: std_stream_capture_logger.py
[`"hello\n"`]: std_stream_capture_logger.py
[`\n`]: std_stream_capture_logger.py
[`close()`]: std_stream_capture_logger.py
[`metadata_containers/run.py`]: ../../metadata_containers/run.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
