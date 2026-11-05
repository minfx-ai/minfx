# gpu

GPU hardware monitoring via NVIDIA NVML for experiment runs.

## Purpose

This module provides GPU hardware monitoring capabilities using NVIDIA NVML.
The GPU monitoring module tracks GPU utilization, memory usage, and power
consumption for NVIDIA GPUs during experiment runs.
[`GPUMonitor`] queries GPU metrics via NVML (NVIDIA Management Library).
The monitor detects GPU card count and per-card utilization percentage.
It reports per-card memory usage in bytes and power consumption.
It also exposes maximum power rating and total GPU memory capacity.
The module gracefully handles NVML errors such as missing drivers or
unsupported GPUs.
It provides informative warnings and continues with default values on
failure.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./gpu_monitor.py` - [`GPUMonitor`] NVML queries for GPU metrics.

## Usages

- [`MetricServiceFactory`] constructs a [`GPUMonitor`] for resource detection
  and gauge sampling.
- [`SystemResourceInfoFactory`] reads card count, memory, and power limits
  via [`GPUMonitor`].
- [`gauges::gpu`] gauges sample utilization, memory, and power through
  [`GPUMonitor`].
- See [`../README.md`] for the parent hardware monitoring system overview.


[`GPUMonitor`]: gpu_monitor.GPUMonitor
[`MetricServiceFactory`]: ../metrics/service/metric_service_factory.py
[`SystemResourceInfoFactory`]: ../resources/system_resource_info_factory.py
[`gauges::gpu`]: ../gauges/gpu.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
