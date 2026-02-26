"""Neptune v3 integration for MinFX.

This module is an alias for minfx.neptune_v2, providing neptune_scale-compatible
API methods while using the neptune_v2 implementation internally.

Usage:
    import minfx.neptune_v3 as neptune

    # Neptune Scale style API (via compatibility aliases):
    run = neptune.init_run(project="workspace/project")
    run.log_configs(data={"config": config_dict}, flatten=True, cast_unsupported=True)
    run.log_metrics(data={"metrics/acc": acc}, step=step)
    run.add_tags(["tag1", "tag2"])
    run.wait_for_processing()  # alias for sync()
    run.wait_for_submission()  # alias for wait()
    run.close()                # alias for stop()

    # Or use native neptune_v2 API directly:
    run["params/lr"] = 0.001
    run["metrics/loss"].append(loss, step=step)
    run.stop()
"""

import minfx.neptune_v2 as _neptune_v2
from minfx.neptune_v2 import *

__all__ = _neptune_v2.__all__

import sys

sys.modules[__name__].__dict__.update(
    {name: getattr(_neptune_v2, name) for name in dir(_neptune_v2) if not name.startswith("_")},
)
