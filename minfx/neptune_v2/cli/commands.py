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

__all__ = ["clear", "status", "sync"]

from typing import (
    TYPE_CHECKING,
)

import click

from minfx.neptune_v2.cli.clear import ClearRunner
from minfx.neptune_v2.cli.path_option import path_option
from minfx.neptune_v2.cli.status import StatusRunner
from minfx.neptune_v2.cli.sync import SyncRunner
from minfx.neptune_v2.internal.backends.hosted_neptune_backend import HostedNeptuneBackend
from minfx.neptune_v2.internal.credentials import Credentials

if TYPE_CHECKING:
    from pathlib import Path


@click.command()
@path_option
def status(path: Path) -> None:
    r"""List synchronized and unsynchronized objects in the given directory. Trashed objects are not listed.

    Minfx stores object data on disk in the '.neptune' directory. If an object executes offline
    or if the network is unavailable as the object executes, the object data can be synchronized
    with the server with this command line utility.

    Examples:
    \b
    # List synchronized and unsynchronized objects in the current directory
    minfx status

    \b
    # List synchronized and unsynchronized objects in directory "foo/bar" without actually syncing
    minfx status --path foo/bar
    """
    backend = HostedNeptuneBackend(Credentials.from_token())

    StatusRunner.status(backend=backend, path=path)


@click.command()
@path_option
@click.option(
    "--object",
    "object_names",
    multiple=True,
    metavar="<object-name>",
    help="object name (workspace/project/short-id or UUID for offline runs) to synchronize.",
)
@click.option(
    "-p",
    "--project",
    "project_name",
    multiple=False,
    metavar="project-name",
    help="project name (workspace/project) where offline runs will be sent",
)
@click.option(
    "--offline-only",
    "offline_only",
    is_flag=True,
    default=False,
    help="synchronize only the offline runs inside '.neptune' directory",
)
def sync(
    path: Path,
    object_names: list[str],
    project_name: str | None,
    offline_only: bool | None,
) -> None:
    r"""Synchronizes objects with unsent data to the server.

    Minfx stores object data on disk in the '.neptune' directory. If an object executes offline
    or if the network is unavailable as the run executes, the object data can be synchronized
    with the server with this command line utility.

    You can list unsynchronized runs with `minfx status`

    Examples:
    \b
    # Synchronize all objects in the current directory
    minfx sync

    \b
    # Synchronize all objects in the given path
    minfx sync --path foo/bar

    \b
    # Synchronize only runs "NPT-42" and "NPT-43" in "workspace/project" in the current directory
    minfx sync --object workspace/project/NPT-42 --object workspace/project/NPT-43

    \b
    # Synchronise all objects in the current directory, sending offline runs to project "workspace/project"
    minfx sync --project workspace/project

    \b
    # Synchronize only the offline run with UUID offline/a1561719-b425-4000-a65a-b5efb044d6bb
    # to project "workspace/project"
    minfx sync --project workspace/project --object offline/a1561719-b425-4000-a65a-b5efb044d6bb

    \b
    # Synchronize only the offline runs
    minfx sync --offline-only

    \b
    # Synchronize only the offline runs to project "workspace/project"
    minfx sync --project workspace/project --offline-only
    """
    backend = HostedNeptuneBackend(Credentials.from_token())

    if offline_only:
        if object_names:
            raise click.BadParameter("--object and --offline-only are mutually exclusive")

        SyncRunner.sync_all_offline(backend=backend, base_path=path, project_name=project_name)

    elif object_names:
        SyncRunner.sync_selected(backend=backend, base_path=path, project_name=project_name, object_names=object_names)
    else:
        SyncRunner.sync_all(backend=backend, base_path=path, project_name=project_name)


@click.command()
@path_option
def clear(path: Path) -> None:
    r"""Clears metadata that has been synchronized or trashed, but is still present in local storage.

    Lists objects and data to be cleared before deleting the data.

    Examples:
    \b
    # Clear junk metadata from local storage
    minfx clear

    \b
    # Clear junk metadata from directory "foo/bar"
    minfx clear --path foo/bar
    """
    backend = HostedNeptuneBackend(Credentials.from_token())

    ClearRunner.clear(backend=backend, path=path)
