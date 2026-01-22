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

__all__ = [
    "detect_async_dir",
    "detect_offline_dir",
    "get_backend_name_for_backend",
    "get_backend_subdirs",
    "get_backend_subdirs_for_token",
    "get_metadata_container",
    "get_project",
    "get_qualified_name",
    "is_multi_backend_directory",
    "is_single_execution_dir_synced",
]

import os
import textwrap
import threading
from typing import (
    TYPE_CHECKING,
    Any,
)

from minfx.neptune_v2.common.exceptions import NeptuneException
from minfx.neptune_v2.core.components.queue.disk_queue import DiskQueue
from minfx.neptune_v2.envs import PROJECT_ENV_NAME
from minfx.neptune_v2.exceptions import (
    MetadataContainerNotFound,
    ProjectNotFound,
)
from minfx.neptune_v2.internal.container_type import ContainerType
from minfx.neptune_v2.internal.id_formats import (
    QualifiedName,
    UniqueId,
)
from minfx.neptune_v2.internal.operation import Operation
from minfx.neptune_v2.internal.utils.backend_name import (
    backend_name_from_url,
    get_backend_name_from_token,
    is_named_backend_directory,
)
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.metadata_containers.structure_version import StructureVersion

if TYPE_CHECKING:
    from pathlib import Path

    from minfx.neptune_v2.internal.backends.api_model import (
        ApiExperiment,
        Project,
    )
    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend

logger = get_logger(with_prefix=False)


def get_metadata_container(
    backend: NeptuneBackend,
    container_id: UniqueId | QualifiedName,
    container_type: ContainerType | None = None,
) -> ApiExperiment | None:
    public_container_type = container_type or "object"
    try:
        return backend.get_metadata_container(container_id=container_id, expected_container_type=container_type)
    except MetadataContainerNotFound:
        logger.warning("Can't fetch %s %s. Skipping.", public_container_type, container_id)
    except NeptuneException as e:
        logger.warning("Exception while fetching %s %s. Skipping.", public_container_type, container_id)
        logger.exception(e)

    return None


_project_name_missing_message = (
    "Project name not provided. Could not synchronize offline runs."
    " To synchronize an offline run, specify the project name with the --project flag"
    f" or by setting the {PROJECT_ENV_NAME} environment variable."
)


def _project_not_found_message(project_name: QualifiedName) -> str:
    return (
        f"Project {project_name} not found. Could not synchronize offline runs."
        " Please ensure you specified the correct project name with the --project flag"
        f" or with the {PROJECT_ENV_NAME} environment variable, or contact Neptune for support."
    )


def get_project(backend: NeptuneBackend, project_name_flag: QualifiedName | None = None) -> Project | None:
    project_name: QualifiedName | None = project_name_flag
    if project_name_flag is None:
        project_name_from_env = os.getenv(PROJECT_ENV_NAME)
        if project_name_from_env is not None:
            project_name = QualifiedName(project_name_from_env)

    if not project_name:
        logger.warning(textwrap.fill(_project_name_missing_message))
        return None
    try:
        return backend.get_project(project_name)
    except ProjectNotFound:
        logger.warning(textwrap.fill(_project_not_found_message(project_name)))
        return None


def get_qualified_name(experiment: ApiExperiment) -> QualifiedName:
    return QualifiedName(f"{experiment.workspace}/{experiment.project_name}/{experiment.sys_id}")


def is_single_execution_dir_synced(execution_path: Path) -> bool:
    def serializer(op: Operation) -> dict[str, Any]:
        return op.to_dict()

    with DiskQueue(execution_path, serializer, Operation.from_dict, threading.RLock()) as disk_queue:
        is_queue_empty: bool = disk_queue.is_empty()

    return is_queue_empty


def detect_async_dir(dir_name: str) -> tuple[ContainerType, UniqueId, StructureVersion]:
    parts = dir_name.split("__")
    if len(parts) == 1:
        return ContainerType.RUN, UniqueId(dir_name), StructureVersion.LEGACY
    if len(parts) == 2:
        return ContainerType(parts[0]), UniqueId(parts[1]), StructureVersion.CHILD_EXECUTION_DIRECTORIES
    if len(parts) == 4 or len(parts) == 5:
        return ContainerType(parts[0]), UniqueId(parts[1]), StructureVersion.DIRECT_DIRECTORY
    raise ValueError(f"Wrong dir format: {dir_name}")


def detect_offline_dir(dir_name: str) -> tuple[ContainerType, UniqueId, StructureVersion]:
    parts = dir_name.split("__")
    if len(parts) == 1:
        return ContainerType.RUN, UniqueId(dir_name), StructureVersion.DIRECT_DIRECTORY
    if len(parts) == 2 or len(parts) == 4:
        return ContainerType(parts[0]), UniqueId(parts[1]), StructureVersion.DIRECT_DIRECTORY
    raise ValueError(f"Wrong dir format: {dir_name}")


def is_multi_backend_directory(path: Path) -> bool:
    """Check if directory contains backend subdirectories (multi-backend structure).

    Multi-backend creates subdirectories with DNS-based names like:
        run__uuid__pid__key/
            neptune2_localhost_8889/
            neptune2_localhost_8890/

    Also supports legacy format with backend_N directories.

    Returns True if directory contains at least one backend subdirectory.
    """
    if not path.is_dir():
        return False
    return any(
        child.is_dir() and (is_named_backend_directory(child.name) or _is_legacy_backend_directory(child.name))
        for child in path.iterdir()
    )


def _is_legacy_backend_directory(name: str) -> bool:
    """Check if a directory name is a legacy backend_N directory."""
    if not name.startswith("backend_"):
        return False
    suffix = name[len("backend_") :]
    return suffix.isdigit()


def get_backend_subdirs(path: Path) -> list[Path]:
    """Get list of backend subdirectories.

    Supports both named backends (neptune2_localhost_8889) and legacy format (backend_N).
    For legacy format, returns directories sorted by backend index.
    For named format, returns directories sorted alphabetically.
    """
    backend_dirs = [
        child
        for child in path.iterdir()
        if child.is_dir() and (is_named_backend_directory(child.name) or _is_legacy_backend_directory(child.name))
    ]

    # Check if we have legacy format (backend_N)
    has_legacy = any(_is_legacy_backend_directory(d.name) for d in backend_dirs)
    if has_legacy:
        return sorted(backend_dirs, key=lambda p: int(p.name.split("_")[1]))

    # Named format - sort alphabetically
    return sorted(backend_dirs, key=lambda p: p.name)


def get_backend_subdirs_for_token(path: Path, api_token: str) -> list[Path]:
    """Get backend subdirectories matching the given API token.

    Args:
        path: The container path containing backend subdirectories.
        api_token: The base64-encoded API token.

    Returns:
        List of paths matching the token's backend, or empty list if no match.
    """
    target_name = get_backend_name_from_token(api_token)
    if not target_name:
        return []

    return [child for child in path.iterdir() if child.is_dir() and child.name == target_name]


def get_backend_name_for_backend(backend: "NeptuneBackend") -> str:
    """Get the backend name derived from a NeptuneBackend's display address.

    Args:
        backend: The NeptuneBackend instance.

    Returns:
        The filesystem-safe backend name.
    """
    return backend_name_from_url(backend.get_display_address())
