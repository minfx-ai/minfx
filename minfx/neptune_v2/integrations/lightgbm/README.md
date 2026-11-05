# lightgbm

LightGBM gradient boosting integration for Neptune experiment tracking.

## Purpose

This module provides integration with the LightGBM gradient boosting framework.
The LightGBM integration enables automatic logging of LightGBM training runs,
including metrics, model parameters, and feature importance.
This integration delegates to the [`neptune-lightgbm`] package for callbacks
and logging implementations.
The integration provides automatic logging of training metrics, model
parameter tracking, feature importance visualization, and callback
integration with LightGBM training.

## Subdirectories / Files

- `./__init__.py` - Package entry that re-exports [`neptune-lightgbm`] symbols.

## Usages

- Install the external dependency with pip install [`neptune-lightgbm`].
- The integration is automatically available when [`neptune-lightgbm`] is
  installed.
- Use LightGBM callbacks through this module to enable Neptune logging.
- See [`../README.md`] for the parent integrations module overview.


[`neptune-lightgbm`]: __init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
