# mosaicml

Integration with MosaicML's training framework for Neptune experiment
tracking.

## Purpose

This module provides integration with MosaicML's training framework.
The MosaicML integration enables tracking of MosaicML training runs, including
metrics, model checkpoints, and training configurations.
It provides automatic logging of training metrics and checkpoint tracking.
It supports training configuration logging and MosaicML callback integration.
This integration requires the [`mosaicml`] package for Composer loggers and
training callbacks.

## Subdirectories / Files

- `./__init__.py` - Package entry that loads MosaicML loggers when [`mosaicml`]
  is installed.

## Usages

- Install [`mosaicml`] with pip before importing this module.
- The integration is automatically available when [`mosaicml`] is installed.
- Use MosaicML-specific loggers through this module.
- See [`../README.md`] for information about Neptune integrations.


[`mosaicml`]: https://pypi.org/project/mosaicml/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
