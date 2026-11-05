# system

System-level resource monitoring via psutil wrappers.

## Purpose

The system module wraps psutil to provide cross-platform access to system
resource information.
It exposes CPU count, CPU usage percent, and virtual memory statistics for
host-level hardware monitoring.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./system_monitor.py` - [`SystemMonitor`] wrapper around psutil for querying
  system resources.

## Usages

- [`gauges::SystemCpuUsageGauge`] and [`gauges::SystemMemoryUsageGauge`] call
  [`SystemMonitor`] for host CPU percent and virtual memory totals.
- [`CGroupMonitor`] receives a [`SystemMonitor`] for host CPU count and memory
  totals when cgroup limits are relative to the host.
- [`SystemResourceInfoFactory`] uses [`SystemMonitor`] for CPU core count and
  total memory at experiment startup.
- [`service::MetricServiceFactory`] wires [`SystemMonitor`] into resource
  detection and gauge construction.
- See [`../README.md`] for the parent hardware monitoring overview.


[`SystemMonitor`]: system_monitor.SystemMonitor
[`gauges::SystemCpuUsageGauge`]: ../gauges/cpu.py
[`gauges::SystemMemoryUsageGauge`]: ../gauges/memory.py
[`CGroupMonitor`]: ../cgroup/cgroup_monitor.py
[`SystemResourceInfoFactory`]: ../resources/system_resource_info_factory.py
[`service::MetricServiceFactory`]: ../metrics/service/metric_service_factory.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
