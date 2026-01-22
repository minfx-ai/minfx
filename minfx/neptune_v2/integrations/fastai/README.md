# Fast.ai Integration

This module provides integration with the Fast.ai deep learning library.

## Purpose

The Fast.ai integration enables automatic logging of Fast.ai training runs, including metrics, model parameters, and learning rate schedules.

## Installation

This integration requires the `neptune-fastai` package:
```bash
pip install neptune-fastai
```

## Functionality

The Fast.ai integration provides:
- Automatic logging of training and validation metrics
- Learning rate schedule tracking
- Model architecture logging
- Callback integration with Fast.ai learners

## Usage

The integration is automatically available when the `neptune-fastai` package is installed. Use Fast.ai callbacks through this module to enable Neptune logging.

## Parent Module

See `../README.md` for information about Neptune integrations.

---
7dcfce5a 2026-01-18T14:43:38
