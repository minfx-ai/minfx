# gauges

Gauge implementations for measuring CPU, memory, and GPU hardware resources.

## Purpose

Gauges are measurement instruments that sample specific hardware metrics at a
point in time.
This module implements gauges for different resource types.
Each [`Gauge`] exposes a name and current value reading for metrics such as CPU
percent, memory bytes, and GPU utilization.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./cpu.py` - System and cgroup CPU usage gauge implementations.
- `./gauge.py` - [`Gauge`] abstract base class defining the gauge interface.
- `./gauge_factory.py` - [`GaugeFactory`] for creating gauge instances by
  mode.
- `./gauge_mode.py` - [`GaugeMode`] enumeration of system and cgroup modes.
- `./gpu.py` - GPU utilization, memory, and power gauge implementations.
- `./memory.py` - System and cgroup memory usage gauge implementations.

## Usages

- [`GaugeFactory`] creates CPU, memory, and GPU gauges based on
  [`GaugeMode`].
- [`service::MetricServiceFactory`] wires [`GaugeFactory`] into metric
  collection during experiment runs.
- [`reports::MetricReporter`] polls gauges periodically to build hardware
  metric reports.
- See [`../README.md`] for the parent hardware monitoring module.


[`Gauge`]: ./gauge.py
[`GaugeFactory`]: ./gauge_factory.py
[`GaugeMode`]: ./gauge_mode.py
[`reports::MetricReporter`]: ../metrics/reports/metric_reporter.py
[`service::MetricServiceFactory`]: ../metrics/service/metric_service_factory.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
