# Kedro Integration

This module provides integration with the Kedro data pipeline framework.

## Purpose

The Kedro integration enables tracking of Kedro pipeline runs, including datasets, parameters, and pipeline metrics.

## Installation

This integration requires the `neptune-kedro` package:
```bash
pip install neptune-kedro
```

## Functionality

The Kedro integration provides:
- Automatic logging of pipeline parameters
- Dataset tracking
- Pipeline execution metrics
- Node-level performance monitoring

## Usage

The integration is automatically available when the `neptune-kedro` package is installed. Configure Kedro hooks through this module to enable Neptune tracking.

## Parent Module

See `../README.md` for information about Neptune integrations.

---
7dcfce5a 2026-01-18T14:43:38
