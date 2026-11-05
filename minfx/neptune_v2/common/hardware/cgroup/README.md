# cgroup

Linux cgroup-based resource monitoring for containerized environments.

## Purpose

The cgroup module enables accurate resource usage tracking when running
experiments inside containers (Docker, Kubernetes, etc.).
It reads cgroup filesystem data to measure CPU and memory within container
limits rather than host system limits.
The monitor tracks memory usage and limits, CPU usage relative to cgroup
quota, and CPU core limits from cgroup allocation.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./cgroup_filesystem_reader.py` - [`CGroupFilesystemReader`] low-level
  reader for cgroup filesystem metrics.
- `./cgroup_monitor.py` - [`CGroupMonitor`] CPU and memory monitoring within
  cgroup limits.

## Usages

- [`gauges::CGroupCpuUsageGauge`] and [`gauges::CGroupMemoryUsageGauge`]
  call [`CGroupMonitor::create`] to sample cgroup CPU and memory usage.
- [`SystemResourceInfoFactory`] uses [`CGroupMonitor::create`] when
  gauge mode is cgroup to report container CPU and memory limits.
- See [`../README.md`] for the parent hardware monitoring overview.


[`CGroupMonitor`]: cgroup_monitor.CGroupMonitor
[`CGroupFilesystemReader`]: cgroup_filesystem_reader.CGroupFilesystemReader
[`CGroupMonitor::create`]: cgroup_monitor.create
[`gauges::CGroupCpuUsageGauge`]: ../gauges/cpu.py
[`gauges::CGroupMemoryUsageGauge`]: ../gauges/memory.py
[`SystemResourceInfoFactory`]: ../resources/system_resource_info_factory.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
