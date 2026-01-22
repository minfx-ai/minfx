# CGroup Monitoring

This module provides Linux cgroup-based resource monitoring for containerized environments.

## Purpose

The cgroup module enables accurate resource usage tracking when running experiments inside containers (Docker, Kubernetes, etc.) by reading cgroup filesystem data.

## Key Components

- `CGroupMonitor`: Monitors CPU and memory usage within cgroup limits
- `CGroupFilesystemReader`: Low-level reader for cgroup filesystem data

## Functionality

The cgroup monitor provides:
- Memory usage and limit tracking within container constraints
- CPU usage percentage relative to allocated CPU quota
- CPU core limit detection based on cgroup quotas
- Accurate resource measurements that respect container resource limits

## Usage

This module is automatically used when experiments run in containerized environments to provide accurate resource metrics that account for container resource limits rather than host system limits.

## Parent Module

See `../README.md` for information about the hardware monitoring system.

---
7dcfce5a 2026-01-18T14:43:38
