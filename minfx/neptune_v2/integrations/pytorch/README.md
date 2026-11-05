# pytorch

PyTorch deep learning framework integration for Neptune experiment tracking.

## Purpose

This module provides integration with the PyTorch deep learning framework.
The PyTorch integration enables automatic logging of PyTorch training runs.
It logs model architecture, gradients, and training metrics.
It tracks parameters, metrics, and model checkpoints.
It integrates with PyTorch hooks and callbacks for Neptune logging.
[`require_installed`] verifies the [`neptune-pytorch`] package before import.
The module re-exports callbacks and helpers from [`neptune_pytorch::impl`].

## Subdirectories / Files

- `./__init__.py` - Entrypoint; re-exports [`neptune_pytorch::impl`].

## Usages

- Install [`neptune-pytorch`] with pip install neptune-pytorch.
- The integration is automatically available when [`neptune-pytorch`] is
  installed.
- Use PyTorch-specific loggers and utilities through this module.
- See [`../README.md`] for information about Neptune integrations.


[`require_installed`]: ../../../internal/utils/requirement_check.py
[`neptune-pytorch`]: neptune_pytorch
[`neptune_pytorch::impl`]: neptune_pytorch.impl
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
