# Transformers Integration

This module provides integration with Hugging Face Transformers library.

## Purpose

The Transformers integration enables tracking of Hugging Face model training, including fine-tuning runs, model configurations, and evaluation metrics.

## Installation

This integration requires the `neptune-transformers` package:
```bash
pip install neptune-transformers
```

## Functionality

The Transformers integration provides:
- Automatic logging of training metrics
- Model configuration tracking
- Tokenizer configuration logging
- Integration with Trainer callbacks
- Model checkpoint management

## Usage

The integration is automatically available when the `neptune-transformers` package is installed. Use Transformers callbacks through this module to track training runs.

## Parent Module

See `../README.md` for information about Neptune integrations.

---
7dcfce5a 2026-01-18T14:43:38
