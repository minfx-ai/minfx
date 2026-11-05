# metadata_containers

This module provides container classes for different Neptune object types.

## Purpose

The metadata containers module implements the main container classes ([`Run`],
[`Project`], [`Model`], [`ModelVersion`]) that users interact with to log and
manage experiment data.
It provides run tracking and experiment logging, project-level operations,
model registry functionality, and model version management.
It supports hierarchical attribute access and operation queuing for backend
synchronization.

## Subdirectories / Files

- `./__init__.py` - Public exports for container classes.
- `./abstract.py` - Abstract base classes for Neptune objects.
- `./metadata_container.py` - Base [`MetadataContainer`] implementation.
- `./model.py` - [`Model`] container for model registry.
- `./model_version.py` - [`ModelVersion`] container.
- `./project.py` - [`Project`] container for project-level operations.
- `./run.py` - [`Run`] container for experiment tracking.
- `./structure_version.py` - [`StructureVersion`] enum for local layout.
- `./utils.py` - Container utility functions including [`parse_dates`].

## Usages

- Users interact with containers as the main Neptune API entry points.
- Create a run with [`neptune.init_run()`], assign parameters with
  run["parameters/learning_rate"], append metrics with
  run["metrics/loss"].append(), then call [`run.stop()`].
- Initialize project-level operations with [`neptune.init_project()`].
- Register models with [`neptune.init_model()`] and manage versions with
  [`neptune.init_model_version()`].
- See [`../README.md`] for the parent neptune_v2 module overview.


[`MetadataContainer`]: metadata_container.MetadataContainer
[`Model`]: model.Model
[`ModelVersion`]: model_version.ModelVersion
[`Project`]: project.Project
[`Run`]: run.Run
[`StructureVersion`]: structure_version.StructureVersion
[`parse_dates`]: utils.parse_dates
[`neptune.init_run()`]: ../__init__.py
[`neptune.init_project()`]: ../__init__.py
[`neptune.init_model()`]: ../__init__.py
[`neptune.init_model_version()`]: ../__init__.py
[`run.stop()`]: run.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
