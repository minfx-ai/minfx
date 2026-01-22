# System Resources

This module provides system resource information and configuration for hardware monitoring.

## Purpose

The resources module collects and provides information about available system resources (CPU cores, memory, GPUs) to configure the hardware monitoring system appropriately.

## Key Components

- `SystemResourceInfo`: Data class containing system resource information
- `SystemResourceInfoFactory`: Factory for detecting and creating system resource info
- `GpuCardIndicesProvider`: Provides GPU card indices for monitoring

## Functionality

This module:
- Detects available CPU cores
- Determines total system memory
- Identifies available GPU cards
- Provides resource information for configuring metrics and gauges

## Usage

This module is used during initialization of the hardware monitoring system to detect available resources and configure appropriate metrics and gauges.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
