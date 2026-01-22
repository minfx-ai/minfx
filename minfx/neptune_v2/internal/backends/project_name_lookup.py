#
# Copyright (c) 2022, Neptune Labs Sp. z o.o.
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
from __future__ import annotations

__all__ = ["project_name_lookup"]

import os
from typing import TYPE_CHECKING

from minfx.neptune_v2.envs import PROJECT_ENV_NAME
from minfx.neptune_v2.exceptions import NeptuneMissingProjectNameException
from minfx.neptune_v2.internal.utils import verify_type
from minfx.neptune_v2.internal.utils.logger import get_logger

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.api_model import Project
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.id_formats import QualifiedName

_logger = get_logger()


def project_name_lookup(backend: NeptuneBackend, name: QualifiedName | None = None) -> Project:
    verify_type("name", name, (str, type(None)))

    if not name:
        name = os.getenv(PROJECT_ENV_NAME)
    if not name:
        available_workspaces = backend.get_available_workspaces()
        available_projects = backend.get_available_projects()

        raise NeptuneMissingProjectNameException(
            available_workspaces=available_workspaces,
            available_projects=available_projects,
        )

    return backend.get_project(name)
