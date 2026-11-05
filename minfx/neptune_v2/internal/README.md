# internal

Internal implementation details of the Neptune client.

## Purpose

The internal module houses the core implementation of Neptune's functionality.
It provides backends, operation processing, hardware monitoring, and various
utilities that power the public Neptune API.
[`operation.py`] defines [`Operation`] types sent to backends.
[`operation_visitor.py`] implements the visitor pattern over operations.
[`value_to_attribute_visitor.py`] converts Python values to Neptune
attributes.
[`background_job.py`] defines the [`BackgroundJob`] base class for periodic
tasks.
[`state.py`] tracks container lifecycle and operation acceptance state.
[`credentials.py`] wraps API tokens and connection settings in
[`Credentials`].

## Subdirectories / Files

- `./artifacts/` - Artifact management, hashing, and storage coordination.
- `./backends/` - Backend implementations for Neptune service communication.
- `./hardware/` - Hardware metric reporting background jobs.
- `./init/` - Initialization defaults and timing thresholds.
- `./notebooks/` - Jupyter notebook integration and comm handling.
- `./operation_processors/` - Async, sync, and offline operation processors.
- `./signals_processing/` - OS signal handling and graceful shutdown.
- `./streams/` - Stdout and stderr stream capture.
- `./threading/` - Daemon thread utilities for background workers.
- `./types/` - Internal type definitions and SDK compatibility helpers.
- `./utils/` - Internal utility functions for paths, logging, and git.
- `./websockets/` - WebSocket coordination and signal background jobs.
- `./__init__.py` - Package marker with no public re-exports.
- `./backgroud_job_list.py` - [`BackgroundJobList`] composite background job.
- `./background_job.py` - [`BackgroundJob`] abstract base class.
- `./constants.py` - Internal constants shared across modules.
- `./container_structure.py` - [`ContainerStructure`] hierarchical path tree.
- `./container_type.py` - [`ContainerType`] enum for run and project kinds.
- `./credentials.py` - [`Credentials`] for API token and proxy configuration.
- `./exceptions.py` - [`NeptuneInternalException`] base internal exception.
- `./extensions.py` - [`load_extensions`] entry-point plugin loader.
- `./id_formats.py` - ID format parsing and validation utilities.
- `./operation.py` - [`Operation`] definitions for attribute mutations.
- `./operation_visitor.py` - [`OperationVisitor`] generic operation visitor.
- `./state.py` - Container and forking state enums.
- `./value_to_attribute_visitor.py` - [`ValueToAttributeVisitor`] value
  converter.

## Usages

- This module is for internal use only.
- Users should interact with Neptune through the public API in parent modules.
- [`operation.py`] operations flow through `./operation_processors/` into
  `./backends/` for server communication.
- [`BackgroundJob`] subclasses in `./hardware/`, `./streams/`, and
  `./websockets/` run periodic monitoring and capture tasks.
- `./signals_processing/` handles graceful shutdown on OS signals.
- `./artifacts/` manages artifact hashing and storage coordination.
- See [`../README.md`] for the parent neptune_v2 module overview.


[`Operation`]: operation.Operation
[`BackgroundJob`]: background_job.BackgroundJob
[`BackgroundJobList`]: backgroud_job_list.BackgroundJobList
[`ContainerStructure`]: container_structure.ContainerStructure
[`ContainerType`]: container_type.ContainerType
[`Credentials`]: credentials.Credentials
[`NeptuneInternalException`]: exceptions.NeptuneInternalException
[`OperationVisitor`]: operation_visitor.OperationVisitor
[`ValueToAttributeVisitor`]: value_to_attribute_visitor.ValueToAttributeVisitor
[`load_extensions`]: extensions.load_extensions
[`operation.py`]: operation.py
[`operation_visitor.py`]: operation_visitor.py
[`value_to_attribute_visitor.py`]: value_to_attribute_visitor.py
[`background_job.py`]: background_job.py
[`state.py`]: state.py
[`credentials.py`]: credentials.py
[`../README.md`]: ../README.md

---
2026-11-05T16:01:08
