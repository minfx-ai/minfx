# pytorch_lightning

Integration with the PyTorch Lightning framework for Neptune experiment
tracking.

## Purpose

The PyTorch Lightning integration enables automatic logging of Lightning
training runs, including metrics, hyperparameters, and model checkpoints.
This integration requires the [`neptune-pytorch-lightning`] package for
Lightning callbacks, loggers, checkpoint management, and multi-GPU training
support.

## Subdirectories / Files

- `./__init__.py` - Package entry that loads [`neptune-pytorch-lightning`] when
  installed.

## Usages

- Install [`neptune-pytorch-lightning`] with pip before importing this module.
- The integration is automatically available when [`neptune-pytorch-lightning`]
  is installed.
- Use the Neptune logger with Lightning trainers.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-pytorch-lightning`]: https://pypi.org/p/neptune-pytorch-lightning/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
