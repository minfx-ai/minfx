# Hardware Metrics

This module provides the core infrastructure for hardware metrics collection and management.

## Purpose

The metrics module defines the data structures and containers for organizing hardware measurements (CPU, GPU, memory, etc.) collected during experiment runs.

## Key Components

- `Metric`: Represents a hardware metric with metadata (name, description, type, unit, range) and associated gauges
- `MetricResourceType`: Enumeration of resource types (CPU, RAM, GPU, GPU_MEMORY, GPU_POWER, OTHER)
- `MetricsContainer`: Container for managing collections of metrics
- `MetricsFactory`: Factory for creating standard metric sets

## Submodules

- `reports/`: Metric reporting functionality
- `service/`: Metric service layer for collection and transmission

## Functionality

The metrics system:
- Defines structured metric metadata
- Groups related gauges into metrics
- Manages collections of metrics for different resource types
- Provides factories for creating standard metric configurations

## Usage

This module is used by the hardware monitoring system to organize and manage all hardware metrics collected during experiment execution.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
