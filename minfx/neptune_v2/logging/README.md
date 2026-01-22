# Logging

This module provides Python logging integration for Neptune.

## Purpose

The logging module enables integration between Python's standard logging module and Neptune, allowing automatic capture of log messages.

## Key Components

- `logger.py`: Neptune logger implementation for Python's logging module

## Functionality

This module provides:
- Integration with Python's logging module
- Automatic log message capture
- Log level filtering
- Structured log formatting

## Usage

Use Neptune's logger handler to capture Python logs:
```python
import logging
from minfx.neptune_v2.logging import NeptuneHandler

logger = logging.getLogger()
logger.addHandler(NeptuneHandler(run=run))
```

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
7dcfce5a 2026-01-18T14:43:38
