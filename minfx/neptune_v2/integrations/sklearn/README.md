# sklearn

Scikit-learn machine learning integration for Neptune experiment tracking.

## Purpose

This module provides integration with the scikit-learn machine learning
library.
The scikit-learn integration enables tracking of scikit-learn models,
including parameters, metrics, and model artifacts.
This integration delegates to the [`neptune-sklearn`] package for callbacks
and logging implementations.
The integration provides model parameter logging, cross-validation results
tracking, feature importance visualization, model serialization and
versioning, and classification and regression metrics.

## Subdirectories / Files

- `./__init__.py` - Package entry that re-exports [`neptune-sklearn`] symbols.

## Usages

- Install the external dependency with pip install [`neptune-sklearn`].
- The integration is automatically available when [`neptune-sklearn`] is
  installed.
- Log scikit-learn models and results through this module.
- See [`../README.md`] for the parent integrations module overview.


[`neptune-sklearn`]: __init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
