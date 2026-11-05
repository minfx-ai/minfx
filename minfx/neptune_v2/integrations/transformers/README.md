# transformers

Hugging Face Transformers integration for Neptune experiment tracking.

## Purpose

This module provides integration with the Hugging Face Transformers library.
The Transformers integration enables tracking of Hugging Face model training.
It supports fine-tuning runs, model configurations, and evaluation metrics.
It logs training metrics, model configuration, and tokenizer configuration.
It integrates with Trainer callbacks for Neptune logging.
It supports model checkpoint management during training.
[`require_installed`] verifies the [`transformers`] package before import.
The module re-exports [`NeptuneCallback`] from [`transformers::integrations`].

## Subdirectories / Files

- `./__init__.py` - Entrypoint; re-exports [`NeptuneCallback`].

## Usages

- Install [`transformers`] with pip install transformers.
- The integration is automatically available when [`transformers`] is
  installed.
- Use Transformers callbacks through this module to track training runs.
- See [`../README.md`] for information about Neptune integrations.


[`require_installed`]: ../../../internal/utils/requirement_check.py
[`transformers`]: transformers
[`NeptuneCallback`]: transformers.integrations.NeptuneCallback
[`transformers::integrations`]: transformers.integrations
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
