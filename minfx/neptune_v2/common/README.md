# common

Shared utilities and components used across the Neptune v2 client.

## Purpose

The common module provides exceptions, environment constants, authentication,
and helper utilities used throughout Neptune.
[`exceptions.py`] defines Neptune-specific error types for API and client
failures.
[`warnings.py`] supplies deprecation and unsupported-type warning helpers.
[`envs.py`] centralizes environment variable names for configuration.
[`oauth.py`] implements OAuth2 token refresh for hosted API clients.
[`git_info.py`] stores git commit metadata attached to experiment runs.
[`patterns.py`] holds shared validation regex patterns.
[`utils.py`] provides general helpers such as proxy and path utilities.
The [`backends/`], [`hardware/`], [`patches/`], [`storage/`], and
[`websockets/`] subpackages cover backend models, resource monitoring,
third-party fixes, file uploads, and live socket communication.

## Subdirectories / Files

- `./backends/` - Backend communication utilities and shared API models.
- `./hardware/` - Hardware resource monitoring for experiment runs.
- `./patches/` - Third-party library patches and workarounds.
- `./storage/` - File storage, chunking, and streaming utilities.
- `./websockets/` - WebSocket communication with automatic reconnection.
- `./__init__.py` - Package marker with no public re-exports.
- `./envs.py` - Environment variable name constants.
- `./exceptions.py` - Common Neptune exception classes.
- `./experiments.py` - Legacy experiment placeholder type.
- `./git_info.py` - Git repository metadata for experiments.
- `./oauth.py` - OAuth2 authentication for hosted API clients.
- `./patterns.py` - Shared regex patterns and constants.
- `./utils.py` - General utility functions.
- `./warnings.py` - Neptune-specific warning helpers.

## Usages

- [`hosted_client.py`] uses [`NeptuneAuthenticator`] from [`oauth.py`].
- [`backend_config.py`] reads [`API_TOKEN_ENV_NAME`] from [`envs.py`].
- [`hw::reporting`] wires gauges and monitors from [`hardware/`] during
  experiment runs.
- CLI and internal modules raise and catch types from [`exceptions.py`].
- See [`../README.md`] for the Neptune v2 client overview.


[`API_TOKEN_ENV_NAME`]: envs.py
[`NeptuneAuthenticator`]: oauth.NeptuneAuthenticator
[`backend_config.py`]: ../../internal/backends/backend_config.py
[`backends/`]: backends/
[`envs.py`]: envs.py
[`exceptions.py`]: exceptions.py
[`git_info.py`]: git_info.py
[`hardware/`]: hardware/
[`hw::reporting`]: ../internal/hardware/hardware_metric_reporting_job.py
[`hosted_client.py`]: ../../internal/backends/hosted_client.py
[`oauth.py`]: oauth.py
[`patterns.py`]: patterns.py
[`patches/`]: patches/
[`storage/`]: storage/
[`utils.py`]: utils.py
[`warnings.py`]: warnings.py
[`websockets/`]: websockets/
[`../README.md`]: ../README.md

---
2026-08-27T14:54:08
