"""MinFX.

This package provides core functionality for the minfx system.
"""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __package_version__ = version("minfx")
except PackageNotFoundError:
    __package_version__ = "unknown"

__author__ = "Minfx Technologies, s.r.o."
__email__ = "contact@minfx.ai"

# Bootstrap value used during minfx.neptune_v2 import.
__version__ = __package_version__

_neptune_v2 = import_module("minfx.neptune_v2")

# Keep top-level imports equivalent to `minfx.neptune_v2` imports.
_neptune_public_names = [str(public_name) for public_name in _neptune_v2.__all__]

for _public_name in _neptune_public_names:
    globals()[_public_name] = getattr(_neptune_v2, _public_name)

neptune_v2 = _neptune_v2
__version__ = _neptune_v2.__version__
__all__ = [str(public_name) for public_name in _neptune_v2.__all__]
__all__ += ["neptune_v2"]


def __getattr__(name: str) -> Any:
    """Mirror unknown package attributes from minfx.neptune_v2."""
    return getattr(_neptune_v2, name)


def __dir__() -> list[str]:
    """Expose neptune_v2 members during introspection."""
    return sorted(set(globals()) | set(dir(_neptune_v2)))
