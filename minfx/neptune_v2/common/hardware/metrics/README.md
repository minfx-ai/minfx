# metrics

Core infrastructure for hardware metrics collection and management.

## Purpose

This module defines data structures and containers for organizing hardware
measurements collected during experiment runs.
[`Metric`] represents a hardware metric with metadata and associated gauges.
[`MetricResourceType`] enumerates resource types such as CPU, RAM, and GPU.
[`MetricsContainer`] manages collections of metrics for different resource
types.
[`MetricsFactory`] creates standard metric sets from system resource info.

## Subdirectories / Files

- `./reports/` - Metric reporting functionality for gauge sampling.
- `./service/` - Metric service layer for collection and transmission.
- `./__init__.py` - Package marker with no public re-exports.
- `./metric.py` - [`Metric`] and [`MetricResourceType`] definitions.
- `./metrics_container.py` - [`MetricsContainer`] for grouped metric access.
- `./metrics_factory.py` - [`MetricsFactory`] for standard metric creation.

## Usages

- [`MetricsFactory::create_metrics_container`] builds a [`MetricsContainer`]
  with CPU, memory, and optional GPU metrics.
- [`service::MetricServiceFactory`] wires [`MetricsFactory`] output into the
  reporting pipeline.
- [`HardwareMetricReportingJob`] starts background hardware monitoring using
  [`MetricsFactory`] and the reports and service subpackages.
- See [`../README.md`] for the parent hardware monitoring overview.


[`Metric`]: metric.Metric
[`MetricResourceType`]: metric.MetricResourceType
[`MetricsContainer`]: metrics_container.MetricsContainer
[`MetricsFactory`]: metrics_factory.MetricsFactory
[`MetricsFactory::create_metrics_container`]: metrics_factory.py
[`service::MetricServiceFactory`]: service/metric_service_factory.py
[`HardwareMetricReportingJob`]: hardware_metric_reporting_job.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
