# Hardware Monitoring

This module provides comprehensive hardware resource monitoring for Neptune experiments.

## Purpose

The hardware monitoring system tracks CPU, GPU, and memory usage during experiment execution, providing insights into resource utilization and helping optimize experiments.

## Submodules

- `cgroup/`: Linux cgroup-based resource monitoring for containers
- `gauges/`: Hardware metric gauges (CPU, memory, GPU)
- `gpu/`: GPU monitoring via NVIDIA NVML
- `metrics/`: Metric definitions and management
- `resources/`: System resource detection and configuration
- `system/`: System-level resource monitoring

## Key Components

- `constants.py`: Hardware monitoring constants

## Functionality

The hardware monitoring system:
- Detects available system resources (CPU cores, memory, GPUs)
- Monitors resource usage in real-time
- Handles containerized environments with cgroup support
- Reports metrics to the Neptune backend
- Provides accurate measurements even in constrained environments

## Usage

Hardware monitoring is automatically enabled when running Neptune experiments, collecting resource metrics in the background without requiring user configuration.

## Parent Module

See `../README.md` for information about the common utilities system.

---
7dcfce5a 2026-01-18T14:43:38
