# tensorboard

Integration with the TensorBoard visualization toolkit for Neptune
experiment tracking.

## Purpose

This module provides integration with the TensorBoard visualization toolkit.
The TensorBoard integration enables importing TensorBoard logs into Neptune,
allowing unified tracking across different experiment tracking tools.
This integration requires the [`neptune-tensorboard`] package for log import,
scalar and histogram conversion, event file parsing, and unified visualization.

## Subdirectories / Files

- `./__init__.py` - Loads [`neptune-tensorboard`] when installed.

## Usages

- Install [`neptune-tensorboard`] with pip before importing this module.
- The integration is automatically available when [`neptune-tensorboard`] is
  installed.
- Import TensorBoard logs through this module's utilities.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-tensorboard`]: https://pypi.org/project/neptune-tensorboard/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
