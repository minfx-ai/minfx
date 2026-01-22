# XGBoost Integration

This module provides integration with the XGBoost gradient boosting library.

## Purpose

The XGBoost integration enables automatic logging of XGBoost training runs, including metrics, model parameters, and feature importance.

## Installation

This integration requires the `neptune-xgboost` package:
```bash
pip install neptune-xgboost
```

## Functionality

The XGBoost integration provides:
- Automatic logging of training metrics
- Model parameter tracking
- Feature importance visualization
- Callback integration with XGBoost training
- Model serialization and versioning

## Usage

The integration is automatically available when the `neptune-xgboost` package is installed. Use XGBoost callbacks through this module to enable Neptune logging.

## Parent Module

See `../README.md` for information about Neptune integrations.

---
7dcfce5a 2026-01-18T14:43:38
