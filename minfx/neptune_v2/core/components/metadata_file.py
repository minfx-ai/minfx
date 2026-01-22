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

__all__ = ["MetadataFile"]

import contextlib
from json import (
    JSONDecodeError,
    dump,
    load,
)
from pathlib import Path
from typing import (
    Any,
    TypeAlias,
)

from minfx.neptune_v2.core.components.abstract import Resource

METADATA_FILE: str = "metadata.json"

# Type alias for JSON-compatible values
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class MetadataFile(Resource):
    def __init__(self, data_path: Path, metadata: dict[str, JsonValue] | None = None):
        self._data_path = data_path
        self._metadata_path: Path = (data_path / METADATA_FILE).resolve(strict=False)
        self._data: dict[str, JsonValue] = self._read_or_default()

        if metadata:
            for key, value in metadata.items():
                self.__setitem__(key, value)
            self.flush()

    @property
    def data_path(self) -> Path:
        return self._data_path

    def __getitem__(self, item: str) -> JsonValue:
        return self._data[item]

    def __setitem__(self, key: str, value: JsonValue) -> None:
        self._data[key] = value

    def flush(self) -> None:
        with self._metadata_path.open("w") as handler:
            dump(self._data, handler, indent=2)

    def _read_or_default(self) -> dict[str, JsonValue]:
        if self._metadata_path.exists():
            try:
                with self._metadata_path.open() as handler:
                    data: dict[str, Any] = load(handler)
                    return data
            except (OSError, JSONDecodeError):
                pass

        return {}

    def cleanup(self) -> None:
        with contextlib.suppress(OSError):
            self._metadata_path.unlink()
