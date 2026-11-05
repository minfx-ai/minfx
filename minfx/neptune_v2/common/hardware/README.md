# hardware

Comprehensive hardware resource monitoring for Neptune experiments.

## Purpose

This module tracks CPU, GPU, and memory usage during experiment execution.
It provides insights into resource utilization and helps optimize experiments.
The system detects available resources such as CPU cores, memory, and GPUs.
It monitors usage in real time and handles containerized environments via
cgroup support.
It reports metrics to the Neptune backend with accurate measurements even in
constrained environments.

## Subdirectories / Files

- `./cgroup/` - Linux cgroup-based resource monitoring for containers.
- `./gauges/` - Hardware metric gauges for CPU, memory, and GPU.
- `./gpu/` - GPU monitoring via NVIDIA NVML.
- `./metrics/` - Metric definitions, reporting, and service layer.
- `./resources/` - System resource detection and configuration.
- `./system/` - System-level resource monitoring via psutil.
- `./__init__.py` - Package marker with no public re-exports.
- `./constants.py` - Shared byte and power unit conversion constants.

## Usages

- Hardware monitoring starts automatically when [`Run`] enables
  [`capture_hardware_metrics`].
- Background hardware collection runs through the metrics, gauges, and service
  subpackages during Neptune experiment runs.
- [`service::MetricServiceFactory`] wires monitors and gauges into the
  reporting pipeline.
- See [`../README.md`] for the parent common utilities overview.


[`Run`]: ../../metadata_containers/run.py
[`capture_hardware_metrics`]: ../../metadata_containers/run.py
[`service::MetricServiceFactory`]: metrics/service/metric_service_factory.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
