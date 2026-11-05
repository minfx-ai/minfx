# utils

Internal utility functions used throughout the Neptune v2 client.

## Purpose

This module collects shared helpers for logging, path handling, image
conversion, git integration, dependency checks, and background jobs.
[`logger.py`] provides colored terminal logging for better readability.
Colors follow log level, with dim timestamps and logger names.
[`MINFX_LOG_COLOR=1`] forces colors on, [`MINFX_LOG_COLOR=0`] forces them off,
and [`NO_COLOR`] disables colors per the no-color.org standard.
[`backend_name.py`] maps backend URLs and tokens to stable directory names.
[`git.py`] and [`source_code.py`] track repository metadata and uploads.
[`images.py`] converts charts and arrays into loggable content.
[`requirement_check.py`] guards optional integration imports.

## Subdirectories / Files

- `./__init__.py` - Public re-exports for type checks, path helpers, and
  encoding utilities.
- `./backend_name.py` - Backend name utilities for multi-backend URL-to-
  directory mapping.
- `./dependency_tracking.py` - Strategies for recording package dependency
  versions on runs.
- `./deprecation.py` - Deprecation decorators for APIs and parameters.
- `./disk_utilization.py` - Disk usage guard decorator for operation
  processors.
- `./experiment_state.py` - [`ExperimentState`] enum mapping API run lifecycle
  values.
- `./generic_attribute_mapper.py` - Maps API attribute results to Python
  values.
- `./git.py` - Git repository metadata, diffs, and uncommitted change
  tracking.
- `./hashing.py` - Hash generation from string descriptors.
- `./images.py` - Image, chart, and pickle content conversion for logging.
- `./iso_dates.py` - ISO-8601 date string parsing.
- `./iteration.py` - Iterable batching utilities.
- `./limits.py` - Custom run ID length and logged image size limit checks.
- `./logger.py` - Colored terminal logging with TTY and environment controls.
- `./paths.py` - Neptune attribute path parsing and joining.
- `./ping_background_job.py` - Background job that pings hosted runs to stay
  alive.
- `./process_killer.py` - Process tree termination for graceful shutdown.
- `./requirement_check.py` - Optional dependency installation checks.
- `./runningmode.py` - Detects interactive shells and Jupyter notebooks.
- `./s3.py` - Boto3 S3 client factory with custom endpoint support.
- `./source_code.py` - Source file upload helpers for runs.
- `./traceback_job.py` - Background job that logs thread tracebacks on demand.
- `./type_protocols.py` - Protocol types for optional visualization libraries.
- `./uncaught_exception_handler.py` - Global uncaught exception logging hook.

## Usages

- Internal backends, attributes, CLI tools, and integrations import helpers
  from this package to avoid duplicating common logic.
- [`get_logger()`] from [`logger.py`] is the standard logging entry point
  across Neptune modules.
- [`require_installed()`] from [`requirement_check.py`] validates optional
  integration dependencies before import.
- [`ensure_disk_not_overutilize`] from [`disk_utilization.py`] wraps sync and
  async operation processors.
- [`PingBackgroundJob`] keeps hosted runs alive during long executions.
- [`ExperimentState`] maps API experiment state values for tables and
  integrations.
- [`get_boto_s3_client()`] from [`s3.py`] configures S3 access for artifact
  drivers.
- See [`../README.md`] for the parent internal module overview.


[`logger.py`]: logger.py
[`backend_name.py`]: backend_name.py
[`git.py`]: git.py
[`source_code.py`]: source_code.py
[`images.py`]: images.py
[`requirement_check.py`]: requirement_check.py
[`MINFX_LOG_COLOR=1`]: logger.py
[`MINFX_LOG_COLOR=0`]: logger.py
[`NO_COLOR`]: logger.py
[`ExperimentState`]: experiment_state.ExperimentState
[`get_logger()`]: logger.get_logger
[`require_installed()`]: requirement_check.require_installed
[`ensure_disk_not_overutilize`]: disk_utilization.ensure_disk_not_overutilize
[`PingBackgroundJob`]: ping_background_job.PingBackgroundJob
[`get_boto_s3_client()`]: s3.get_boto_s3_client
[`s3.py`]: s3.py
[`disk_utilization.py`]: disk_utilization.py
[`../README.md`]: ../README.md

---
2026-11-04T18:28:20
