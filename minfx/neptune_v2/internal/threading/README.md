# threading

Threading utilities for Neptune background operations.

## Purpose

The threading module provides daemon thread management for background jobs.
[`Daemon`] is a thread base class with pause, resume, interrupt, and sleep
control.
[`ConnectionRetryWrapper`] retries work on connection loss with exponential
backoff.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./daemon.py` - [`Daemon`] thread base class and [`ConnectionRetryWrapper`]
  decorator.

## Usages

- Neptune background jobs subclass [`Daemon`] and implement [`work`].
- Hardware monitoring, async operation processing, signal handling, and stream
  capture use this module.
- [`ConnectionRetryWrapper`] wraps daemon work methods to survive transient
  backend connection failures.
- See [`../README.md`] for the parent internal module overview.


[`Daemon`]: daemon.Daemon
[`ConnectionRetryWrapper`]: daemon.Daemon.ConnectionRetryWrapper
[`work`]: daemon.Daemon.work
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
