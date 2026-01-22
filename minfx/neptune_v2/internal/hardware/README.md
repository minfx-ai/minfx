# Internal Hardware

This module provides internal hardware monitoring coordination.

## Purpose

The internal hardware module coordinates hardware metric collection and reporting as a background job.

## Key Components

- `hardware_metric_reporting_job.py`: Background job for periodic hardware metric collection and reporting

## Functionality

This module provides:
- Background job scheduling for hardware metrics
- Coordination between metric collection and backend reporting
- Lifecycle management for hardware monitoring

## Usage

This module is used internally by the Neptune client to run hardware monitoring in the background during experiment execution.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
7dcfce5a 2026-01-18T14:43:38
