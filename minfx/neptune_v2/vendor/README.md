# vendor

Vendored third-party libraries bundled with Neptune.

## Purpose

The vendor module includes copies of third-party libraries bundled with
Neptune to avoid external dependencies or to use modified versions.
[`pynvml.py`] provides NVIDIA GPU monitoring without a separate pynvml
installation.
[`lib_programname.py`] supplies program name detection for various
environments.
These libraries are self-contained and not intended for direct user import.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./lib_programname.py` - Program name detection utilities.
- `./pynvml.py` - Python bindings for NVIDIA Management Library (NVML).

## Usages

- [`gpu_monitor.py`] imports [`pynvml.py`] for NVML GPU metrics during runs.
- [`source_code.py`] and [`git_ref.py`] import [`lib_programname.py`] for
  executed script path detection.
- See [`../README.md`] for information about the Neptune v2 client.


[`pynvml.py`]: pynvml.py
[`lib_programname.py`]: lib_programname.py
[`gpu_monitor.py`]: ../common/hardware/gpu/gpu_monitor.py
[`source_code.py`]: ../internal/utils/source_code.py
[`git_ref.py`]: ../types/atoms/git_ref.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
