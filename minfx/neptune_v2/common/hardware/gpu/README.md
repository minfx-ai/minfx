# GPU Monitoring

This module provides GPU hardware monitoring capabilities using NVIDIA NVML.

## Purpose

The GPU monitoring module tracks GPU utilization, memory usage, and power consumption for NVIDIA GPUs during experiment runs.

## Key Components

- `GPUMonitor`: Main class for querying GPU metrics via NVML (NVIDIA Management Library)

## Functionality

The GPU monitor provides:
- GPU card count detection
- Per-card utilization percentage
- Per-card memory usage in bytes
- Per-card power consumption
- Maximum power rating per card
- Total GPU memory capacity

## Error Handling

The module gracefully handles NVML errors (missing drivers, unsupported GPUs, etc.) and provides informative warnings while continuing to operate with default values.

## Usage

This module is used by the hardware metrics system to collect GPU-related metrics when NVIDIA GPUs are available in the system.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
