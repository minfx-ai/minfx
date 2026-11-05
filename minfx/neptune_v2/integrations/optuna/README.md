# optuna

Integration with the Optuna hyperparameter optimization framework for Neptune
experiment tracking.

## Purpose

This module provides integration with the Optuna hyperparameter optimization
framework.
The Optuna integration enables tracking of hyperparameter optimization studies,
including trial parameters, metrics, and optimization history.
This integration requires the [`neptune-optuna`] package for trial logging,
optimization history tracking, and parameter importance visualization.

## Subdirectories / Files

- `./__init__.py` - Package entry that loads [`neptune-optuna`] when installed.

## Usages

- Install [`neptune-optuna`] with pip before importing this module.
- The integration is automatically available when [`neptune-optuna`] is
  installed.
- Use Optuna callbacks through this module to track optimization studies.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-optuna`]: https://pypi.org/project/neptune-optuna/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
