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

__all__ = ["Table"]

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Generator,
    TypeAlias,
)

from minfx.neptune_v2.exceptions import MetadataInconsistency
from minfx.neptune_v2.integrations.pandas import to_pandas
from minfx.neptune_v2.internal.backends.api_model import (
    AttributeType,
    AttributeWithProperties,
    LeaderboardEntry,
)
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.paths import (
    join_paths,
    parse_path,
)
from minfx.neptune_v2.internal.utils.run_state import RunState

if TYPE_CHECKING:
    import pandas as pd

    from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.typing import ProgressBarType


logger = get_logger()

# Type alias for all possible attribute values returned by get_attribute_value
AttributeValue: TypeAlias = float | int | bool | str | datetime | set[str] | None


class TableEntry:
    def __init__(
        self,
        backend: NeptuneBackend,
        container_type: ContainerType,
        _id: str,
        attributes: list[AttributeWithProperties],
    ):
        self._backend = backend
        self._container_type = container_type
        self._id = _id
        self._attributes = attributes

    def __getitem__(self, path: str) -> LeaderboardHandler:
        return LeaderboardHandler(table_entry=self, path=path)

    def get_attribute_type(self, path: str) -> AttributeType:
        for attr in self._attributes:
            if attr.path == path:
                return attr.type
        raise ValueError(f"Could not find {path} attribute")

    def get_attribute_value(self, path: str) -> AttributeValue:
        for attr in self._attributes:
            if attr.path == path:
                _type = attr.type
                if _type == AttributeType.RUN_STATE:
                    return RunState.from_api(attr.properties.get("value")).value
                if _type in (
                    AttributeType.FLOAT,
                    AttributeType.INT,
                    AttributeType.BOOL,
                    AttributeType.STRING,
                    AttributeType.DATETIME,
                ):
                    return attr.properties.get("value")
                if _type in (AttributeType.FLOAT_SERIES, AttributeType.STRING_SERIES):
                    return attr.properties.get("last")
                if _type == AttributeType.IMAGE_SERIES:
                    raise MetadataInconsistency("Cannot get value for image series.")
                if _type == AttributeType.FILE:
                    raise MetadataInconsistency("Cannot get value for file attribute. Use download() instead.")
                if _type == AttributeType.FILE_SET:
                    raise MetadataInconsistency("Cannot get value for file set attribute. Use download() instead.")
                if _type == AttributeType.STRING_SET:
                    values = attr.properties.get("values")
                    return set(values) if values else set()
                if _type == AttributeType.GIT_REF:
                    commit = attr.properties.get("commit")
                    return commit.get("commitId") if commit else None
                if _type == AttributeType.NOTEBOOK_REF:
                    return attr.properties.get("notebookName")
                if _type == AttributeType.ARTIFACT:
                    return attr.properties.get("hash")
                logger.error(
                    "Attribute type %s not supported in this version, yielding None. Recommended client upgrade.",
                    _type,
                )
                return None
        raise ValueError(f"Could not find {path} attribute")

    def download_file_attribute(
        self,
        path: str,
        destination: str | None,
        progress_bar: ProgressBarType | None = None,
    ) -> None:
        for attr in self._attributes:
            if attr.path == path:
                _type = attr.type
                if _type == AttributeType.FILE:
                    self._backend.download_file(
                        container_id=self._id,
                        container_type=self._container_type,
                        path=parse_path(path),
                        destination=destination,
                        progress_bar=progress_bar,
                    )
                    return
                raise MetadataInconsistency(f"Cannot download file from attribute of type {_type}")
        raise ValueError(f"Could not find {path} attribute")

    def download_file_set_attribute(
        self,
        path: str,
        destination: str | None,
        progress_bar: ProgressBarType | None = None,
    ) -> None:
        for attr in self._attributes:
            if attr.path == path:
                _type = attr.type
                if _type == AttributeType.FILE_SET:
                    self._backend.download_file_set(
                        container_id=self._id,
                        container_type=self._container_type,
                        path=parse_path(path),
                        destination=destination,
                        progress_bar=progress_bar,
                    )
                    return
                raise MetadataInconsistency(f"Cannot download ZIP archive from attribute of type {_type}")
        raise ValueError(f"Could not find {path} attribute")


class LeaderboardHandler:
    def __init__(self, table_entry: TableEntry, path: str) -> None:
        self._table_entry = table_entry
        self._path = path

    def __getitem__(self, path: str) -> LeaderboardHandler:
        return LeaderboardHandler(table_entry=self._table_entry, path=join_paths(self._path, path))

    def get(self) -> AttributeValue:
        return self._table_entry.get_attribute_value(path=self._path)

    def download(self, destination: str | None) -> None:
        attr_type = self._table_entry.get_attribute_type(self._path)
        if attr_type == AttributeType.FILE:
            return self._table_entry.download_file_attribute(self._path, destination)
        if attr_type == AttributeType.FILE_SET:
            return self._table_entry.download_file_set_attribute(path=self._path, destination=destination)
        raise MetadataInconsistency(f"Cannot download file from attribute of type {attr_type}")


class Table:
    def __init__(
        self,
        backend: NeptuneBackend,
        container_type: ContainerType,
        entries: Generator[LeaderboardEntry, None, None],
    ) -> None:
        self._backend = backend
        self._entries = entries
        self._container_type = container_type
        self._iterator = iter(entries if entries else ())

    def to_rows(self) -> list[TableEntry]:
        return list(self)

    def __iter__(self) -> Table:
        return self

    def __next__(self) -> TableEntry:
        entry = next(self._iterator)

        return TableEntry(
            backend=self._backend,
            container_type=self._container_type,
            _id=entry.id,
            attributes=entry.attributes,
        )

    def to_pandas(self) -> pd.DataFrame:
        return to_pandas(self)
