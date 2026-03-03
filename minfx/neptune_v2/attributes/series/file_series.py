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
from enum import Enum
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
from minfx.neptune_v2.exceptions import FileNotFound
from minfx.neptune_v2.internal.operation import (
    ClearFileLog,
    ClearHtmlLog,
    ClearImageLog,
    FileSeriesValue,
    HtmlValue,
    ImageValue,
    LogFiles,
    LogHtml,
    LogImages,
    LogOperation,
    Operation,
)
from minfx.neptune_v2.internal.types.file_types import FileType
from minfx.neptune_v2.internal.utils import base64_encode
from minfx.neptune_v2.internal.utils.iteration import get_batches
from minfx.neptune_v2.internal.utils.limits import image_size_exceeds_limit_for_logging
from minfx.neptune_v2.types import File
from minfx.neptune_v2.types.series.file_series import FileSeries as FileSeriesVal

if TYPE_CHECKING:
    from minfx.neptune_v2.typing import ProgressBarType

Val = FileSeriesVal
Data = File


class _FileContentType(Enum):
    """Type of file content for routing to appropriate series."""

    IMAGE = "image"
    HTML = "html"
    GENERIC = "generic"


class FileSeries(Series[Val, Data, LogOperation], max_batch_size=1, operation_cls=LogImages):
    """File series that auto-detects content type and routes to appropriate backend series.

    Supports:
    - Images (PNG, JPEG, etc.) -> ImageSeries backend
    - HTML files -> HtmlSeries backend
    - Other files -> FileSeries backend
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._detected_type: _FileContentType | None = None

    def _detect_file_type(self, file: File) -> _FileContentType:
        """Detect the type of file content."""
        extension = file.extension
        if extension:
            ext_lower = extension.lower().lstrip(".")
            if ext_lower == "html" or ext_lower == "htm":
                return _FileContentType.HTML
            if ext_lower in ("png", "jpg", "jpeg", "gif", "bmp", "webp", "tiff", "ico"):
                return _FileContentType.IMAGE

        file_content = self._get_file_content(file)
        if file_content:
            try:
                Image.open(io.BytesIO(file_content))
                return _FileContentType.IMAGE
            except UnidentifiedImageError:
                pass
            if file_content.startswith(b"<!") or file_content.startswith(b"<html") or b"<html" in file_content[:1000]:
                return _FileContentType.HTML

        return _FileContentType.GENERIC

    def _get_file_content(self, file: File) -> bytes:
        """Get the raw content of a file."""
        if file.file_type is FileType.LOCAL_FILE:
            if not pathlib.Path(file.path).exists():
                raise FileNotFound(file.path)
            with pathlib.Path(file.path).open("rb") as f:
                return f.read()
        return file.content or b""

    def _get_base64_content(self, file: File) -> str:
        """Get base64-encoded content of a file."""
        file_content = self._get_file_content(file)
        if self._detected_type == _FileContentType.IMAGE:
            if image_size_exceeds_limit_for_logging(len(file_content)):
                file_content = b""
        return base64_encode(file_content)

    def _get_log_operations_from_value(self, value: Val) -> list[LogOperation]:
        """Override to detect file type and create appropriate operation."""
        if not value.values:
            return []

        first_file = value.values[0]
        self._detected_type = self._detect_file_type(first_file)

        if self._detected_type == _FileContentType.IMAGE:
            return self._create_image_operations(value)
        elif self._detected_type == _FileContentType.HTML:
            return self._create_html_operations(value)
        else:
            return self._create_file_operations(value)

    def _create_image_operations(self, value: Val) -> list[LogImages]:
        """Create LogImages operations for image content."""
        mapped_values = [
            ImageValue(
                data=self._get_base64_content(val),
                name=value.name,
                description=value.description,
            )
            for val in value.values
        ]
        values_with_step_and_ts = zip(mapped_values, value.steps, value.timestamps)
        log_values = [LogImages.ValueType(val, step=step, ts=ts) for val, step, ts in values_with_step_and_ts]
        return [LogImages(self._path, chunk) for chunk in get_batches(log_values, batch_size=self.max_batch_size)]

    def _create_html_operations(self, value: Val) -> list[LogHtml]:
        """Create LogHtml operations for HTML content."""
        mapped_values = [
            HtmlValue(
                data=self._get_base64_content(val),
                name=value.name,
                description=value.description,
            )
            for val in value.values
        ]
        values_with_step_and_ts = zip(mapped_values, value.steps, value.timestamps)
        log_values = [LogHtml.ValueType(val, step=step, ts=ts) for val, step, ts in values_with_step_and_ts]
        return [LogHtml(self._path, chunk) for chunk in get_batches(log_values, batch_size=self.max_batch_size)]

    def _create_file_operations(self, value: Val) -> list[LogFiles]:
        """Create LogFiles operations for generic file content."""
        mapped_values = [
            FileSeriesValue(
                data=self._get_base64_content(val),
                name=value.name,
                description=value.description,
                extension=val.extension,
            )
            for val in value.values
        ]
        values_with_step_and_ts = zip(mapped_values, value.steps, value.timestamps)
        log_values = [LogFiles.ValueType(val, step=step, ts=ts) for val, step, ts in values_with_step_and_ts]
        return [LogFiles(self._path, chunk) for chunk in get_batches(log_values, batch_size=self.max_batch_size)]

    def _get_clear_operation(self) -> Operation:
        """Return appropriate clear operation based on detected type."""
        if self._detected_type == _FileContentType.HTML:
            return ClearHtmlLog(self._path)
        elif self._detected_type == _FileContentType.GENERIC:
            return ClearFileLog(self._path)
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
