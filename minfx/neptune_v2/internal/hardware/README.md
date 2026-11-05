# hardware

Internal hardware monitoring coordination for the Neptune client.

## Purpose

The internal hardware module coordinates hardware metric collection and
reporting as a background job.
[`HardwareMetricReportingJob`] runs periodic sampling of system and GPU
metrics and logs them to experiment attributes.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./hardware_metric_reporting_job.py` - [`HardwareMetricReportingJob`]
  background job for periodic hardware metric collection and reporting.

## Usages

- The Neptune client starts [`HardwareMetricReportingJob`] during experiment
  execution to monitor hardware in the background.
- The job creates float series attributes under the monitoring namespace for
  each hardware gauge.
- See [`../README.md`] for the parent internal module overview.


[`HardwareMetricReportingJob`]: hardware_metric_reporting_job.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
