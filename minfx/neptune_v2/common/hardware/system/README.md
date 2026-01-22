# System Monitoring

This module provides system-level resource monitoring capabilities.

## Purpose

The system monitoring module wraps system-level APIs (psutil) to provide cross-platform access to system resource information.

## Key Components

- `SystemMonitor`: Wrapper around psutil for querying system resources

## Functionality

The system monitor provides:
- CPU count and usage information
- Virtual memory statistics
- System-wide resource metrics

## Usage

This module is used by other hardware monitoring components (cgroup monitor, gauges) to access system-level resource information.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
