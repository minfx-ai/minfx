# signals_processing

Internal signal handling for async operation batch monitoring and callbacks.

## Purpose

The signals processing module tracks async operation batch lifecycle events.
It detects lag and stalled progress, then invokes user-configured callbacks.
[`SignalsProcessor`] consumes queued signals on a daemon thread.
[`CallbacksMonitor`] wires that processor into Neptune background jobs.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./background_job.py` - [`CallbacksMonitor`] background job for signal
  monitoring.
- `./signals.py` - Signal dataclasses and [`SignalsVisitor`] handler
  interface.
- `./signals_processor.py` - [`SignalsProcessor`] queue consumer and callback
  dispatch.
- `./utils.py` - Helpers that enqueue batch lifecycle signals.

## Usages

- Neptune starts [`CallbacksMonitor`] as a background job during client
  initialization.
- Operation processors enqueue batch signals through helpers in [`utils.py`].
- [`SignalsProcessor`] invokes lag and no-progress callbacks when thresholds
  are exceeded.
- See [`../README.md`] for the parent internal module overview.


[`SignalsProcessor`]: signals_processor.SignalsProcessor
[`CallbacksMonitor`]: background_job.CallbacksMonitor
[`SignalsVisitor`]: signals.SignalsVisitor
[`utils.py`]: utils.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
