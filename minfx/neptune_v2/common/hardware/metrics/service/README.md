# service

Service layer for hardware metrics collection and backend reporting.

## Purpose

This package coordinates hardware metric sampling, report generation, and
backend upload during experiment runs.
[`MetricServiceFactory`] wires gauges, metrics, and
[`reports::MetricReporter`] instances into a ready [`MetricService`].
[`MetricService::report_and_send`] samples gauges at a timestamp and sends
reports through the Neptune backend.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./metric_service.py` - [`MetricService`] orchestration and backend upload.
- `./metric_service_factory.py` - [`MetricServiceFactory`] for configured
  service construction.

## Usages

- [`MetricServiceFactory::create`] registers metrics with the backend and
  returns a [`MetricService`] bound to an experiment.
- [`MetricService::report_and_send`] is called periodically to sample gauges
  and push hardware metric reports.
- The parent [`../README.md`] metrics module lists this package as the
  service layer for collection and transmission.


[`MetricService`]: metric_service.MetricService
[`MetricServiceFactory`]: metric_service_factory.MetricServiceFactory
[`MetricService::report_and_send`]: metric_service.report_and_send
[`MetricServiceFactory::create`]: metric_service_factory.create
[`reports::MetricReporter`]: ../reports/metric_reporter.MetricReporter
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
