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

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Callable,
    Iterable,
    NamedTuple,
)

from minfx.neptune_v2.cli.containers import (
    AsyncContainer,
    ExecutionDirectory,
    OfflineContainer,
)
from minfx.neptune_v2.cli.utils import (
    detect_async_dir,
    detect_offline_dir,
    get_backend_name_for_backend,
    get_backend_subdirs,
    get_metadata_container,
    is_multi_backend_directory,
    is_single_execution_dir_synced,
)
from minfx.neptune_v2.constants import (
    ASYNC_DIRECTORY,
    OFFLINE_DIRECTORY,
)
from minfx.neptune_v2.internal.utils.backend_name import is_named_backend_directory
from minfx.neptune_v2.metadata_containers.structure_version import StructureVersion

if TYPE_CHECKING:
    from pathlib import Path

    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import UniqueId


class CollectedContainers(NamedTuple):
    async_containers: list[AsyncContainer]
    offline_containers: list[OfflineContainer]
    synced_containers: list[AsyncContainer]
    unsynced_containers: list[AsyncContainer]
    not_found_containers: list[AsyncContainer]


def collect_containers(*, path: Path, backend: NeptuneBackend) -> CollectedContainers:
    if not path.is_dir():
        return CollectedContainers(
            async_containers=[],
            offline_containers=[],
            synced_containers=[],
            unsynced_containers=[],
            not_found_containers=[],
        )

    async_containers: list[AsyncContainer] = []
    if (path / ASYNC_DIRECTORY).exists():
        async_containers = list(collect_async_containers(path=path, backend=backend))

    offline_containers = []
    if (path / OFFLINE_DIRECTORY).exists():
        offline_containers = list(collect_offline_containers(path=path))

    return CollectedContainers(
        async_containers=async_containers,
        offline_containers=offline_containers,
        synced_containers=[x for x in async_containers if x.synced],
        unsynced_containers=[x for x in async_containers if not x.synced and x.found is True],
        not_found_containers=[x for x in async_containers if x.found is False],
    )


def collect_async_containers(*, path: Path, backend: NeptuneBackend) -> Iterable[AsyncContainer]:
    container_to_execution_dirs = collect_by_container(base_path=path / ASYNC_DIRECTORY, detect_by=detect_async_dir)
    backend_name = get_backend_name_for_backend(backend)

    for (container_type, container_id), execution_dirs in container_to_execution_dirs.items():
        # Filter execution dirs to only those matching current backend (for named backends)
        # Keep all dirs if they don't have named backend structure (legacy format)
        matching_dirs = [
            ed for ed in execution_dirs if not is_named_backend_directory(ed.path.name) or ed.path.name == backend_name
        ]

        if not matching_dirs:
            continue  # No data for this backend

        experiment = get_metadata_container(backend=backend, container_type=container_type, container_id=container_id)
        found = experiment is not None

        yield AsyncContainer(
            container_id=container_id,
            container_type=container_type,
            found=found,
            experiment=experiment,
            execution_dirs=matching_dirs,
        )


def collect_offline_containers(*, path: Path) -> Iterable[OfflineContainer]:
    container_to_execution_dirs = collect_by_container(base_path=path / OFFLINE_DIRECTORY, detect_by=detect_offline_dir)

    for (container_type, container_id), execution_dirs in container_to_execution_dirs.items():
        yield OfflineContainer(
            container_id=container_id,
            container_type=container_type,
            execution_dirs=execution_dirs,
            found=False,
        )


def collect_child_directories(base_path: Path, structure_version: StructureVersion) -> list[Path]:
    if structure_version in {StructureVersion.CHILD_EXECUTION_DIRECTORIES, StructureVersion.LEGACY}:
        return [base_path / r.name for r in base_path.iterdir()]
    if structure_version == StructureVersion.DIRECT_DIRECTORY:
        # Check for multi-backend structure (backend_0/, backend_1/, etc.)
        if is_multi_backend_directory(base_path):
            return get_backend_subdirs(base_path)
        return [base_path]
    raise ValueError(f"Unknown structure version {structure_version}")


def collect_by_container(
    *, base_path: Path, detect_by: Callable[[str], tuple[ContainerType, UniqueId, StructureVersion]]
) -> dict[tuple[ContainerType, UniqueId], list[ExecutionDirectory]]:
    container_to_execution_dirs: dict[tuple[ContainerType, UniqueId], list[ExecutionDirectory]] = defaultdict(list)

    for child_path in base_path.iterdir():
        container_type, unique_id, structure_version = detect_by(child_path.name)
        execution_dirs = collect_child_directories(child_path, structure_version)
        for execution_dir in execution_dirs:
            parent = execution_dir.parent if structure_version == StructureVersion.CHILD_EXECUTION_DIRECTORIES else None
            container_to_execution_dirs[(container_type, unique_id)].append(
                ExecutionDirectory(
                    path=execution_dir,
                    synced=is_single_execution_dir_synced(execution_dir),
                    structure_version=structure_version,
                    parent=parent,
                )
            )

    return container_to_execution_dirs
