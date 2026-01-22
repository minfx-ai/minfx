# Metric Reports

This module provides functionality for reporting hardware metrics collected during experiment runs.

## Purpose

The reports module handles the collection and formatting of hardware metric data into structured reports that can be sent to the backend for tracking and visualization.

## Key Components

- `MetricReport`: Named tuple containing a metric and its collected values
- `MetricValue`: Named tuple representing a single metric measurement with timestamp, running time, gauge name, and value
- `MetricReporter`: Interface for generating metric reports from gauges
- `MetricReporterFactory`: Factory for creating metric reporter instances

## Usage

This module is used internally by the metric service to generate periodic reports of hardware metrics (CPU, GPU, memory usage, etc.) during experiment execution.

## Parent Module

See `../README.md` for information about the metrics system.

---
7dcfce5a 2026-01-18T14:43:38
