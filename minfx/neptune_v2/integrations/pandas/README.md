# pandas

Integration with the Pandas data analysis library for Neptune experiment
tracking.

## Purpose

This module provides integration with the Pandas data analysis library.
The Pandas integration enables logging of Pandas DataFrames and Series as
Neptune artifacts, facilitating data tracking and versioning.
This integration requires the [`neptune-pandas`] package for DataFrame
logging, CSV and other format support, data profiling, and DataFrame
comparison utilities.

## Subdirectories / Files

- `./__init__.py` - Package entry with [`to_pandas`] for Table conversion.

## Usages

- Install [`neptune-pandas`] with pip before importing this module.
- The integration is automatically available when [`neptune-pandas`] is
  installed.
- Log DataFrames through this module's utilities.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-pandas`]: https://pypi.org/project/neptune-pandas/
[`to_pandas`]: __init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
