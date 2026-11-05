# notebooks

Jupyter notebook integration for Neptune checkpoint tracking and kernel
communication.

## Purpose

The internal notebooks module handles detection and integration with Jupyter
notebooks.
It tracks cell execution and extracts notebook metadata when running inside
IPython.
It creates backend checkpoints and notifies the Jupyter kernel when checkpoints
are created.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./comm.py` - [`send_checkpoint_created`] and [`MessageType`] for Jupyter
  kernel communication.
- `./notebooks.py` - [`create_checkpoint`] for IPython notebook checkpoint
  creation.

## Usages

- The Neptune client uses this module when running inside Jupyter notebooks.
- [`create_checkpoint`] creates a backend checkpoint and notifies the kernel
  once per cell execution.
- [`send_checkpoint_created`] publishes checkpoint metadata over the Neptune
  IPython comm target.
- See [`../README.md`] for the parent internal module overview.


[`create_checkpoint`]: notebooks.create_checkpoint
[`send_checkpoint_created`]: comm.send_checkpoint_created
[`MessageType`]: comm.MessageType
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
