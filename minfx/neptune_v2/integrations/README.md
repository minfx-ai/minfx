# Integrations

This module provides integrations with popular machine learning frameworks and tools.

## Purpose

The integrations module enables Neptune to work seamlessly with various ML frameworks, providing automatic logging and tracking capabilities.

## Available Integrations

### Deep Learning Frameworks
- `pytorch/`: PyTorch integration
- `pytorch_lightning/`: PyTorch Lightning integration
- `tensorflow_keras/`: TensorFlow/Keras integration
- `fastai/`: Fast.ai integration

### ML Libraries
- `sklearn/`: Scikit-learn integration
- `xgboost/`: XGBoost integration
- `lightgbm/`: LightGBM integration

### Hyperparameter Optimization
- `optuna/`: Optuna integration

### Computer Vision
- `detectron2/`: Detectron2 integration

### Data Science Tools
- `pandas/`: Pandas integration
- `prophet/`: Prophet integration

### MLOps & Pipelines
- `kedro/`: Kedro integration
- `sacred/`: Sacred integration

### Cloud & Infrastructure
- `aws/`: AWS integration
- `mosaicml/`: MosaicML integration

### Visualization
- `tensorboard/`: TensorBoard integration

### NLP
- `transformers/`: Hugging Face Transformers integration

## Key Components

- `python_logger.py`: Python logging integration
- `utils.py`: Integration utility functions

## Installation

Each integration requires its own package:
```bash
pip install neptune-pytorch
pip install neptune-sklearn
# etc.
```

## Usage

Import and use integration-specific functionality through the respective submodules. Each integration provides callbacks, loggers, or utilities specific to its framework.

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
7dcfce5a 2026-01-18T14:43:38
