# sacred

Integration with the Sacred experiment management framework.

## Purpose

This module provides integration with the Sacred experiment management
framework.
The Sacred integration enables tracking of Sacred experiments.
It includes configurations, metrics, and artifacts.
[`require_installed`] verifies the [`neptune-sacred`] package before import.
The module re-exports observers and helpers from [`neptune_sacred::impl`].

## Subdirectories / Files

- `./__init__.py` - Entrypoint; re-exports [`neptune_sacred::impl`].

## Usages

- Install [`neptune-sacred`] with pip install neptune-sacred.
- The integration is automatically available when [`neptune-sacred`] is
  installed.
- Use Sacred observers through this module to track experiments.
- See [`../README.md`] for information about Neptune integrations.


[`require_installed`]: ../../../internal/utils/requirement_check.py
[`neptune-sacred`]: neptune_sacred
[`neptune_sacred::impl`]: neptune_sacred.impl
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
