"""Neptune integration for MinFX.

This module temporarily re-exports the neptune v3 (also called Neptune Scale) package, allowing it to be accessed as:
    import minfx.neptune_v3
"""

import neptune_scale as _neptune_scale
from neptune_scale import *

# Re-export the neptune module's attributes
__all__ = list(getattr(_neptune_scale, "__all__", [name for name in dir(_neptune_scale) if not name.startswith("_")]))

# Make the module behave like neptune when accessed
import sys

sys.modules[__name__].__dict__.update(
    {name: getattr(_neptune_scale, name) for name in dir(_neptune_scale) if not name.startswith("_")},
)
