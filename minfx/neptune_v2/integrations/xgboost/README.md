# xgboost

XGBoost gradient boosting integration for Neptune experiment tracking.

## Purpose

This module provides integration with the XGBoost gradient boosting library.
The XGBoost integration enables automatic logging of XGBoost training runs,
including metrics, model parameters, and feature importance.
This integration delegates to the [`neptune-xgboost`] package for callbacks
and logging implementations.
The integration provides automatic logging of training metrics, model
parameter tracking, feature importance visualization, and callback
integration with XGBoost training.

## Subdirectories / Files

- `./__init__.py` - Package entry that re-exports [`neptune-xgboost`] symbols.

## Usages

- Install the external dependency with pip install [`neptune-xgboost`].
- The integration is automatically available when [`neptune-xgboost`] is
  installed.
- Use XGBoost callbacks through this module to enable Neptune logging.
- See [`../README.md`] for the parent integrations module overview.


[`neptune-xgboost`]: __init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
