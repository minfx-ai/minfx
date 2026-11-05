# integrations

Integrations with popular machine learning frameworks and tools for Neptune.

## Purpose

The integrations module enables Neptune to work seamlessly with various ML
frameworks, providing automatic logging and tracking capabilities.
The [`aws/`], [`detectron2/`], [`fastai/`], [`kedro/`], [`lightgbm/`],
[`mosaicml/`], [`optuna/`], [`pandas/`], [`prophet/`], [`pytorch/`],
[`pytorch_lightning/`], [`sacred/`], [`sklearn/`], [`tensorboard/`],
[`tensorflow_keras/`], [`transformers/`], and [`xgboost/`] subpackages cover
deep learning, ML libraries, hyperparameter search, data science, MLOps,
cloud, visualization, and NLP tooling.
[`python_logger.py`] provides a logging handler that forwards Python log
records to Neptune runs.
[`utils.py`] supplies shared helpers for integration modules.

## Subdirectories / Files

- `./aws/` - AWS integration for artifact storage and cloud tracking.
- `./detectron2/` - Detectron2 object detection framework integration.
- `./fastai/` - Fast.ai deep learning library integration.
- `./kedro/` - Kedro data pipeline framework integration.
- `./lightgbm/` - LightGBM gradient boosting integration.
- `./mosaicml/` - MosaicML training framework integration.
- `./optuna/` - Optuna hyperparameter optimization integration.
- `./pandas/` - Pandas DataFrame and Series logging integration.
- `./prophet/` - Prophet time series forecasting integration.
- `./pytorch/` - PyTorch deep learning framework integration.
- `./pytorch_lightning/` - PyTorch Lightning training integration.
- `./sacred/` - Sacred experiment management integration.
- `./sklearn/` - Scikit-learn machine learning integration.
- `./tensorboard/` - TensorBoard log import integration.
- `./tensorflow_keras/` - TensorFlow and Keras training integration.
- `./transformers/` - Hugging Face Transformers training integration.
- `./xgboost/` - XGBoost gradient boosting integration.
- `./__init__.py` - Package marker with no public re-exports.
- `./python_logger.py` - Python logging handler for Neptune runs.
- `./utils.py` - Shared integration utility functions.

## Usages

- Install the integration-specific package for each framework, such as
  [`neptune-pytorch`] or [`neptune-sklearn`].
- Import and use integration-specific functionality through the respective
  submodules.
- Each integration provides callbacks, loggers, or utilities specific to its
  framework.
- Use [`python_logger.py`] to forward standard library log records to a run.
- See [`../README.md`] for information about the Neptune v2 client.


[`aws/`]: aws/
[`detectron2/`]: detectron2/
[`fastai/`]: fastai/
[`kedro/`]: kedro/
[`lightgbm/`]: lightgbm/
[`mosaicml/`]: mosaicml/
[`neptune-pytorch`]: https://pypi.org/project/neptune-pytorch/
[`neptune-sklearn`]: https://pypi.org/project/neptune-sklearn/
[`optuna/`]: optuna/
[`pandas/`]: pandas/
[`prophet/`]: prophet/
[`python_logger.py`]: python_logger.py
[`pytorch/`]: pytorch/
[`pytorch_lightning/`]: pytorch_lightning/
[`sacred/`]: sacred/
[`sklearn/`]: sklearn/
[`tensorboard/`]: tensorboard/
[`tensorflow_keras/`]: tensorflow_keras/
[`transformers/`]: transformers/
[`utils.py`]: utils.py
[`xgboost/`]: xgboost/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
