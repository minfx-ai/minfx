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

import sys
import warnings
from importlib.metadata import entry_points

import click

from minfx.neptune_v2.cli.commands import (
    clear,
    status,
    sync,
)


@click.group()
def main() -> None:
    pass


main.add_command(sync)
main.add_command(status)
main.add_command(clear)

# Load plugins using importlib.metadata (replaces deprecated pkg_resources)
if sys.version_info >= (3, 10):
    plugin_eps = entry_points(group="minfx.plugins")
else:
    plugin_eps = entry_points().get("minfx.plugins", [])

for entry_point in plugin_eps:
    # loading an entry_point may fail and this
    # will cause all CLI commands to fail.
    # So, we load the plug-ins in try and except block.
    try:
        loaded_plugin = entry_point.load()
        main.add_command(loaded_plugin, entry_point.name)
    except Exception as e:
        warnings.warn(f"Failed to load minfx plug-in `{entry_point.name}` with exception: {e}", stacklevel=2)
