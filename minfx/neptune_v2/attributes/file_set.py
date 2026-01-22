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

__all__ = ["FileSet"]

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Iterable,
)

from minfx.neptune_v2.attributes.attribute import Attribute
from minfx.neptune_v2.internal.operation import (
    DeleteFiles,
    UploadFileSet,
)
from minfx.neptune_v2.internal.utils import (
    verify_collection_type,
    verify_type,
)
from minfx.neptune_v2.types.file_set import FileSet as FileSetVal

if TYPE_CHECKING:
    from minfx.neptune_v2.api.dtos import FileEntry
    from minfx.neptune_v2.typing import ProgressBarType


class FileSet(Attribute):
    def assign(self, value: FileSetVal | str | Iterable[str], *, wait: bool = False) -> None:
        verify_type("value", value, (FileSetVal, str, Iterable))
        if isinstance(value, FileSetVal):
            value = value.file_globs
        elif isinstance(value, str):
            value = [value]
        else:
            verify_collection_type("value", value, str)
        self._enqueue_upload_operation(value, reset=True, wait=wait)

    def upload_files(self, globs: str | Iterable[str], *, wait: bool = False) -> None:
        if isinstance(globs, str):
            globs = [globs]
        else:
            verify_collection_type("globs", globs, str)
        self._enqueue_upload_operation(globs, reset=False, wait=wait)

    def delete_files(self, paths: str | Iterable[str], *, wait: bool = False) -> None:
        if isinstance(paths, str):
            paths = [paths]
        else:
            verify_collection_type("paths", paths, str)
        with self._container.lock():
            self._enqueue_operation(DeleteFiles(self._path, set(paths)), wait=wait)

    def _enqueue_upload_operation(self, globs: Iterable[str], *, reset: bool, wait: bool):
        with self._container.lock():
            abs_file_globs = [str(Path(file_glob).resolve()) for file_glob in globs]
            self._enqueue_operation(UploadFileSet(self._path, abs_file_globs, reset=reset), wait=wait)

    def download(
        self,
        destination: str | None = None,
        progress_bar: ProgressBarType | None = None,
    ) -> None:
        verify_type("destination", destination, (str, type(None)))
        self._backend.download_file_set(self._container_id, self._container_type, self._path, destination, progress_bar)

    def list_fileset_files(self, path: str | None = None) -> list[FileEntry]:
        path = path or ""
        return self._backend.list_fileset_files(self._path, self._container_id, path)
