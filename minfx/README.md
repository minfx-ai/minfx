# minfx

Python package sources for Minato compatibility clients and wrappers.

## Purpose

Provide the main package entrypoint and Neptune client compatibility modules
used by downstream scripts and integrations.

## Subdirectories / Files

- `./neptune_v2/` - Legacy Neptune-compatible client implementation.
- `./__init__.py` - Package initialization and exported package metadata.
- `./neptune_v3.py` - Neptune Scale-compatible client module.

## Usages

- Import package modules in user scripts that need Neptune compatibility APIs.
- Use `./neptune_v2/` for legacy Neptune workflows and integrations.
- Use `./neptune_v3.py` for Neptune Scale workflows.
- Refer to [README](../README.md) for installation and development workflows.

---
2026-11-05T16:01:08
