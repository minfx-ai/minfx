# reports

Hardware metric report types and reporters for periodic gauge sampling.

## Purpose

This module formats hardware gauge readings into structured report payloads.
[`reports::MetricReport`] pairs a [`metrics::Metric`] with sampled
[`reports::MetricValue`] rows.
[`reports::MetricReporter`] reads gauges at a timestamp and builds those
reports.
[`reports::MetricReporterFactory`] creates reporters anchored to a run start
time.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./metric_report.py` - [`reports::MetricReport`] and
  [`reports::MetricValue`] namedtuple definitions.
- `./metric_reporter.py` - [`reports::MetricReporter`] gauge sampling logic.
- `./metric_reporter_factory.py` - [`reports::MetricReporterFactory`] for
  reporter construction.

## Usages

- [`service::MetricServiceFactory`] builds a [`reports::MetricReporter`] via
  [`reports::MetricReporterFactory`].
- [`service::MetricService`] calls [`MetricReporter::report`] and sends the
  results to the Neptune backend.


[`reports::MetricReport`]: ./metric_report.py
[`reports::MetricValue`]: ./metric_report.py
[`reports::MetricReporter`]: ./metric_reporter.py
[`reports::MetricReporterFactory`]: ./metric_reporter_factory.py
[`metrics::Metric`]: ../metric.py
[`service::MetricService`]: ../service/metric_service.py
[`service::MetricServiceFactory`]: ../service/metric_service_factory.py
[`MetricReporter::report`]: ./metric_reporter.py

---
2026-08-07T13:46:32
