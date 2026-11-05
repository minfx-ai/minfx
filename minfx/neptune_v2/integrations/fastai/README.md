# fastai

Fast.ai deep learning library integration for Neptune experiment tracking.

## Purpose

This module provides integration with the Fast.ai deep learning library.
The Fast.ai integration enables automatic logging of Fast.ai training runs.
It logs training and validation metrics, model parameters, and learning
rate schedules.
It tracks learning rate schedules and model architecture details.
It integrates with Fast.ai learner callbacks for Neptune logging.
[`require_installed`] verifies the [`neptune-fastai`] package before import.
The module re-exports callbacks and helpers from [`neptune_fastai::impl`].

## Subdirectories / Files

- `./__init__.py` - Entrypoint; re-exports [`neptune_fastai::impl`].

## Usages

- Install [`neptune-fastai`] with pip install neptune-fastai.
- The integration is automatically available once [`neptune-fastai`] is
  installed.
- Use Fast.ai callbacks through this module to enable Neptune logging.
- See [`../README.md`] for information about Neptune integrations.


[`require_installed`]: ../../../internal/utils/requirement_check.py
[`neptune-fastai`]: neptune_fastai
[`neptune_fastai::impl`]: neptune_fastai.impl
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
