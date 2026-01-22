# Hardware Gauges

This module provides gauge implementations for measuring various hardware resources.

## Purpose

Gauges are measurement instruments that sample specific hardware metrics at a point in time. This module implements gauges for different resource types.

## Key Components

- `Gauge`: Abstract base class defining the gauge interface
- `GaugeMode`: Enumeration of gauge operating modes
- `GaugeFactory`: Factory for creating gauge instances
- `cpu.py`: CPU usage gauges
- `memory.py`: Memory usage gauges
- `gpu.py`: GPU usage and memory gauges

## Functionality

Each gauge:
- Has a descriptive name
- Provides current value readings
- Samples specific hardware metrics (CPU %, memory bytes, GPU utilization, etc.)

## Usage

Gauges are created by the metrics system and polled periodically to collect hardware resource measurements during experiment execution.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
