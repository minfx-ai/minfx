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

__all__ = ["upload_source_code"]

import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
)

from minfx.neptune_v2.attributes import constants as attr_consts
from minfx.neptune_v2.common.storage.storage_utils import normalize_file_name
from minfx.neptune_v2.common.utils import is_ipython
from minfx.neptune_v2.internal.utils import (
    does_paths_share_common_drive,
    get_absolute_paths,
    get_common_root,
)
from minfx.neptune_v2.vendor.lib_programname import (
    empty_path,
    get_path_executed_script,
)

if TYPE_CHECKING:
    from minfx.neptune_v2 import Run


def upload_source_code(source_files: list[str] | None, run: Run) -> None:
    entrypoint_filepath = get_path_executed_script()

    if not is_ipython() and entrypoint_filepath != empty_path and Path(entrypoint_filepath).is_file():
        if source_files is None:
            entrypoint = Path(entrypoint_filepath).name
            source_files = str(entrypoint_filepath)
        elif not source_files:
            entrypoint = Path(entrypoint_filepath).name
        else:
            common_root = get_common_root(get_absolute_paths(source_files))
            entrypoint_filepath = str(Path(entrypoint_filepath).resolve())

            if common_root is not None and does_paths_share_common_drive([common_root, entrypoint_filepath]):
                entrypoint_filepath = normalize_file_name(os.path.relpath(path=entrypoint_filepath, start=common_root))

            entrypoint = normalize_file_name(entrypoint_filepath)

        run[attr_consts.SOURCE_CODE_ENTRYPOINT_ATTRIBUTE_PATH] = entrypoint

    if source_files is not None:
        run[attr_consts.SOURCE_CODE_FILES_ATTRIBUTE_PATH].upload_files(source_files)
