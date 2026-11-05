# resources

System resource detection and configuration for hardware monitoring.

## Purpose

The resources module collects and provides information about available system
resources (CPU cores, memory, GPUs) to configure the hardware monitoring system
appropriately.
[`SystemResourceInfo`] holds detected CPU, memory, and GPU capacity.
[`SystemResourceInfoFactory`] builds that snapshot from system and GPU monitors.
[`GPUCardIndicesProvider`] resolves which GPU cards are visible for monitoring.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./gpu_card_indices_provider.py` - [`GPUCardIndicesProvider`] for resolving
  GPU card indices from CUDA_VISIBLE_DEVICES.
- `./system_resource_info.py` - [`SystemResourceInfo`] data class with CPU,
  memory, and GPU resource fields.
- `./system_resource_info_factory.py` - [`SystemResourceInfoFactory`] for
  detecting and creating system resource info.

## Usages

- [`SystemResourceInfoFactory::create`] builds [`SystemResourceInfo`] from
  system and GPU monitors for a gauge mode.
- [`MetricServiceFactory::create`] uses [`SystemResourceInfoFactory`] during
  hardware monitoring initialization.
- [`MetricsFactory`] reads [`SystemResourceInfo`] to decide which GPU metrics
  to register.
- See [`../README.md`] for the parent hardware monitoring overview.


[`SystemResourceInfo`]: ./system_resource_info.py
[`SystemResourceInfoFactory`]: ./system_resource_info_factory.py
[`GPUCardIndicesProvider`]: ./gpu_card_indices_provider.py
[`SystemResourceInfoFactory::create`]: ./system_resource_info_factory.py
[`MetricServiceFactory::create`]: ../metrics/service/metric_service_factory.py
[`MetricsFactory`]: ../metrics/metrics_factory.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
