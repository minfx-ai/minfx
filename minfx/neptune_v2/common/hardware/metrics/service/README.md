# Metric Service

This module provides the service layer for hardware metrics collection and reporting.

## Purpose

The metric service coordinates the collection of hardware metrics, generation of reports, and transmission of metric data to the Neptune backend.

## Key Components

- `MetricService`: Main service class that orchestrates metric reporting and backend communication
- `MetricServiceFactory`: Factory for creating configured metric service instances

## Functionality

The metric service:
- Collects hardware metrics at regular intervals
- Generates metric reports using the metric reporter
- Sends reports to the Neptune backend for storage and visualization

## Usage

This module is used internally by the hardware monitoring system to manage the lifecycle of metric collection during experiment runs.

## Parent Module

See `../README.md` for information about the metrics system.

---
7dcfce5a 2026-01-18T14:43:38
