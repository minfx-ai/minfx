# detectron2

Detectron2 object detection framework integration for Neptune experiment
tracking.

## Purpose

This module provides integration with Facebook's Detectron2 object detection
framework.
The Detectron2 integration enables automatic logging of Detectron2 training
runs, including model configurations, metrics, and outputs.
It requires the [`neptune-detectron2`] package for callbacks, loggers, and
Detectron2-specific tracking utilities.
The integration supports training metric logging, model configuration
tracking, checkpoint management, and detection result visualization.

## Subdirectories / Files

- `./__init__.py` - Package entry that requires [`neptune_detectron2`] and
  re-exports its implementation API.

## Usages

- Install the integration with pip install neptune-detectron2.
- The integration is automatically available when the [`neptune-detectron2`]
  package is installed.
- Use Detectron2-specific callbacks and loggers through this module to log
  training metrics, configurations, checkpoints, and visualizations.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-detectron2`]: neptune_detectron2
[`neptune_detectron2`]: neptune_detectron2
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
