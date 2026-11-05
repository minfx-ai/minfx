# prophet

Integration with Facebook's Prophet time series forecasting library.

## Purpose

This module provides integration with Facebook's Prophet time series
forecasting library.
The Prophet integration enables tracking of Prophet forecasting models.
It includes model parameters, forecasts, and diagnostic plots.
This integration requires the [`neptune-prophet`] package for automatic
logging of model parameters, forecast visualization, diagnostic plot
tracking, and model performance metrics.

## Subdirectories / Files

- `./__init__.py` - Package entry that loads [`neptune-prophet`] when installed.

## Usages

- Install [`neptune-prophet`] with pip before importing this module.
- The integration is automatically available when [`neptune-prophet`] is
  installed.
- Log Prophet models and forecasts through this module.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-prophet`]: https://pypi.org/project/neptune-prophet/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
