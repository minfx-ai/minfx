#
# Copyright (c) 2024, Neptune Labs Sp. z o.o.
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

__all__ = [
    "DependencyTrackingStrategy",
    "FileDependenciesStrategy",
    "InferDependenciesStrategy",
]

from abc import (
    ABC,
    abstractmethod,
)
from importlib.metadata import (
    Distribution,
    distributions,
)
import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
)

from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.types import File

if TYPE_CHECKING:
    from minfx.neptune_v2 import Run

logger = get_logger()


class DependencyTrackingStrategy(ABC):
    @abstractmethod
    def log_dependencies(self, run: Run) -> None: ...


class InferDependenciesStrategy(DependencyTrackingStrategy):
    def log_dependencies(self, run: Run) -> None:
        dependencies = []

        def sorting_key_func(d: Distribution) -> str:
            _name = d.metadata["Name"]
            return _name.lower() if isinstance(_name, str) else ""

        dists = sorted(distributions(), key=sorting_key_func)

        for dist in dists:
            if dist.metadata["Name"]:
                dependencies.append(f"{dist.metadata['Name']}=={dist.metadata['Version']}")

        dependencies_str = "\n".join(dependencies)

        if dependencies_str:
            run["source_code/requirements"].upload(File.from_content(dependencies_str))


class FileDependenciesStrategy(DependencyTrackingStrategy):
    def __init__(self, path: str | os.PathLike):
        self._path = path

    def log_dependencies(self, run: Run) -> None:
        if Path(self._path).is_file():
            run["source_code/requirements"].upload(self._path)
        else:
            logger.warning("File '%s' does not exist - skipping dependency file upload.", self._path)
