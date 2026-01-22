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

__all__ = ["FileSeries"]

import io
import pathlib
from typing import (
    TYPE_CHECKING,
    Collection,
    Iterable,
)

from PIL import (
    Image,
    UnidentifiedImageError,
)

from minfx.neptune_v2.attributes.series.series import Series
from minfx.neptune_v2.exceptions import (
    FileNotFound,
    OperationNotSupported,
)
from minfx.neptune_v2.internal.operation import (
    ClearImageLog,
    ImageValue,
    LogImages,
    Operation,
)
from minfx.neptune_v2.internal.types.file_types import FileType
from minfx.neptune_v2.internal.utils import base64_encode
from minfx.neptune_v2.internal.utils.limits import image_size_exceeds_limit_for_logging
from minfx.neptune_v2.types import File
from minfx.neptune_v2.types.series.file_series import FileSeries as FileSeriesVal

if TYPE_CHECKING:
    from minfx.neptune_v2.typing import ProgressBarType

Val = FileSeriesVal
Data = File
LogOperation = LogImages


class FileSeries(Series[Val, Data, LogOperation], max_batch_size=1, operation_cls=LogOperation):
    @classmethod
    def _map_series_val(cls, value: Val) -> list[ImageValue]:
        return [
            ImageValue(
                data=cls._get_base64_image_content(val),
                name=value.name,
                description=value.description,
            )
            for val in value.values
        ]

    def _get_clear_operation(self) -> Operation:
        return ClearImageLog(self._path)

    def _data_to_value(
        self,
        values: Iterable[File],
        steps: Collection[float] | None = None,
        timestamps: Collection[float] | None = None,
    ) -> Val:
        return FileSeriesVal(values, steps=steps, timestamps=timestamps)

    def _is_value_type(self, value: object) -> bool:
        return isinstance(value, FileSeriesVal)

    @staticmethod
    def _get_base64_image_content(file: File) -> str:
        if file.file_type is FileType.LOCAL_FILE:
            if not pathlib.Path(file.path).exists():
                raise FileNotFound(file.path)
            with pathlib.Path(file.path).open("rb") as image_file:
                file_content = File.from_stream(image_file).content
        else:
            file_content = file.content

        try:
            with Image.open(io.BytesIO(file_content)):
                ...
        except UnidentifiedImageError:
            raise OperationNotSupported(
                "FileSeries supports only image files for now. Other file types will be implemented in future."
            ) from None

        if image_size_exceeds_limit_for_logging(len(file_content)):
            file_content = b""

        return base64_encode(file_content)

    def download(self, destination: str | None, progress_bar: ProgressBarType | None = None) -> None:
        target_dir = self._get_destination(destination)
        item_count = self._backend.get_image_series_values(
            self._container_id, self._container_type, self._path, 0, 1
        ).totalItemCount
        for i in range(item_count):
            self._backend.download_file_series_by_index(
                self._container_id, self._container_type, self._path, i, target_dir, progress_bar
            )

    def download_last(self, destination: str | None) -> None:
        target_dir = self._get_destination(destination)
        item_count = self._backend.get_image_series_values(
            self._container_id, self._container_type, self._path, 0, 1
        ).totalItemCount
        if item_count > 0:
            self._backend.download_file_series_by_index(
                self._container_id,
                self._container_type,
                self._path,
                item_count - 1,
                target_dir,
                progress_bar=None,
            )
        else:
            raise ValueError("Unable to download last file - series is empty")

    def _get_destination(self, destination: str | None) -> str:
        target_dir = destination
        if destination is None:
            target_dir = str(pathlib.Path("neptune") / self._path[-1])
        pathlib.Path(target_dir).resolve().mkdir(parents=True, exist_ok=True)
        return target_dir
