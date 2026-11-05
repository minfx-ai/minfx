# tensorflow_keras

TensorFlow and Keras deep learning framework integration for Neptune experiment
tracking.

## Purpose

This module provides integration with the TensorFlow and Keras deep learning
frameworks.
The TensorFlow/Keras integration enables automatic logging of training runs.
It logs model architecture, metrics, and training progress.
[`require_installed`] verifies the [`neptune-tensorflow-keras`] package before
import.
The module re-exports callbacks and helpers from
[`neptune_tensorflow_keras::impl`].

## Subdirectories / Files

- `./__init__.py` - Entrypoint; re-exports [`neptune_tensorflow_keras::impl`].

## Usages

- Install [`neptune-tensorflow-keras`] with pip before importing this module.
- The integration is automatically available when [`neptune-tensorflow-keras`]
  is installed.
- Use Keras callbacks through this module to enable Neptune logging.
- See [`../README.md`] for information about Neptune integrations.


[`require_installed`]: ../../../internal/utils/requirement_check.py
[`neptune-tensorflow-keras`]: neptune_tensorflow_keras
[`neptune_tensorflow_keras::impl`]: neptune_tensorflow_keras.impl
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
