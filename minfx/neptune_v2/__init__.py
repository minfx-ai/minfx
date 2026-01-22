#
# Copyright (c) 2023, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Neptune v2 (legacy) client bundled with minfx.

This module provides the Neptune v2 client directly, eliminating
the need for an external 'neptune' package dependency.

Usage:
    import minfx.neptune_v2 as neptune

    run = neptune.init_run(project="workspace/project")
    run["params/lr"] = 0.001

There are four kinds of Neptune objects: run, model, model version, and project.
They help you track, store, and visualize metadata related to your model-training experiments.
The package contains the functions and constructors needed to initialize the objects.
You can either create new objects or connect to existing ones (to, for example, fetch or add more metadata).

Functions:
    init_run()
    init_model()
    init_model_version()
    init_project()

Classes:
    Run
    Model
    ModelVersion
    Project

Constants:
    ANONYMOUS_API_TOKEN
"""

__all__ = [
    "ANONYMOUS_API_TOKEN",
    "BackendConfig",
    "Model",
    "ModelVersion",
    "Project",
    "Run",
    "__version__",
    "attributes",
    "exceptions",
    "init_model",
    "init_model_version",
    "init_project",
    "init_run",
    "management",
]


from minfx.neptune_v2 import attributes, exceptions, management
from minfx.neptune_v2.common.patches import apply_patches
from minfx.neptune_v2.constants import ANONYMOUS_API_TOKEN
from minfx.neptune_v2.internal.backends.backend_config import BackendConfig
from minfx.neptune_v2.internal.extensions import load_extensions
from minfx.neptune_v2.metadata_containers import (
    Model,
    ModelVersion,
    Project,
    Run,
)
from minfx.neptune_v2.version import __version__

# Apply patches of external libraries
apply_patches()
load_extensions()

init_run = Run
init_model = Model
init_model_version = ModelVersion
init_project = Project
