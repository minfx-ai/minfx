# Metadata Containers

This module provides container classes for different Neptune object types.

## Purpose

The metadata containers module implements the main container classes (Run, Project, Model, ModelVersion) that users interact with to log and manage experiment data.

## Key Components

- `abstract.py`: Abstract base class for all metadata containers
- `metadata_container.py`: Base metadata container implementation
- `run.py`: Run container for experiment tracking
- `project.py`: Project container for project-level operations
- `model.py`: Model container for model registry
- `model_version.py`: Model version container
- `structure_version.py`: Structure version tracking
- `utils.py`: Container utility functions

## Functionality

This module provides:
- Run tracking and experiment logging
- Project-level operations
- Model registry functionality
- Model version management
- Hierarchical attribute access
- Operation queuing and synchronization

## Usage

Users interact with these containers as the main Neptune API:
```python
import neptune

run = neptune.init_run()
run["parameters/learning_rate"] = 0.001
run["metrics/loss"].append(0.5)
run.stop()

project = neptune.init_project()
model = neptune.init_model()
```

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
848aecbd 2026-01-22T01:06:03
