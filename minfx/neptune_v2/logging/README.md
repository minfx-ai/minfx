# logging

This module provides Python logging integration for Neptune.

## Purpose

The logging module enables integration between Python's standard logging
module and Neptune.
It supplies [`Logger`] for writing messages to Neptune string-series
attributes on a run or project container.

## Subdirectories / Files

- `./__init__.py` - Package exports for [`Logger`].
- `./logger.py` - Neptune string-series logger for container attributes.

## Usages

- [`NeptuneHandler`] in integrations attaches to Python loggers and forwards
  records through [`Logger`].
- Internal stream capture imports [`Logger`] to persist stdout and stderr on
  active runs.
- See [`../README.md`] for the parent neptune_v2 module overview.


[`Logger`]: logger.py
[`NeptuneHandler`]: ../integrations/python_logger.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
