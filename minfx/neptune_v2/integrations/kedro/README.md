# kedro

Integration with the Kedro data pipeline framework for Neptune tracking.

## Purpose

This module provides Kedro integration for Neptune experiment tracking.
The integration enables tracking of Kedro pipeline runs.
It logs datasets, parameters, and pipeline metrics.
The package entry re-exports symbols from [`kedro_neptune`] after verifying
the optional dependency is installed.

## Subdirectories / Files

- `./__init__.py` - Package entry that re-exports [`kedro_neptune`] symbols
  after dependency check.

## Usages

- Install [`neptune-kedro`] to enable Kedro tracking with Neptune.
- Import from this module to access Kedro Neptune hooks and callbacks.
- Configure Kedro hooks through this module to enable Neptune tracking.
- See [`../README.md`] for the parent integrations module overview.


[`neptune-kedro`]: https://pypi.org/project/neptune-kedro/
[`kedro_neptune`]: kedro_neptune
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
