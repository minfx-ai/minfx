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

__all__ = ["ArtifactDriver", "ArtifactDriversMap", "ArtifactFileData", "ArtifactFileType", "ArtifactMetadataSerializer"]

import abc
from dataclasses import dataclass
import enum
import typing

from minfx.neptune_v2.exceptions import (
    NeptuneUnhandledArtifactSchemeException,
    NeptuneUnhandledArtifactTypeException,
)

if typing.TYPE_CHECKING:
    import pathlib


class ArtifactFileType(enum.Enum):
    S3 = "S3"
    LOCAL = "Local"


class ArtifactMetadataSerializer:
    @staticmethod
    def serialize(metadata: dict[str, str]) -> list[dict[str, str]]:
        return [{"key": k, "value": v} for k, v in sorted(metadata.items())]

    @staticmethod
    def deserialize(metadata: list[dict[str, str]]) -> dict[str, str]:
        return {f"{key_value.get('key')}": f"{key_value.get('value')}" for key_value in metadata}


@typing.runtime_checkable
class ArtifactFileDTO(typing.Protocol):
    """Protocol for artifact file DTO from backend."""

    @property
    def filePath(self) -> str: ...
    @property
    def fileHash(self) -> str: ...
    @property
    def type(self) -> str: ...
    @property
    def size(self) -> int | None: ...
    @property
    def metadata(self) -> list[object]: ...


@dataclass
class ArtifactFileData:
    file_path: str
    file_hash: str
    type: str
    metadata: dict[str, str]
    size: int | None = None

    @classmethod
    def from_dto(cls, artifact_file_dto: ArtifactFileDTO) -> ArtifactFileData:
        return cls(
            file_path=artifact_file_dto.filePath,
            file_hash=artifact_file_dto.fileHash,
            type=artifact_file_dto.type,
            size=artifact_file_dto.size,
            metadata=ArtifactMetadataSerializer.deserialize(
                [{"key": str(m.key), "value": str(m.value)} for m in artifact_file_dto.metadata]  # type: ignore[attr-defined]
            ),
        )

    def to_dto(self) -> dict:
        return {
            "filePath": self.file_path,
            "fileHash": self.file_hash,
            "type": self.type,
            "size": self.size,
            "metadata": ArtifactMetadataSerializer.serialize(self.metadata),
        }


class ArtifactDriversMap:
    _implementations: list[type[ArtifactDriver]] = []

    @classmethod
    def match_path(cls, path: str) -> type[ArtifactDriver]:
        for artifact_driver in cls._implementations:
            if artifact_driver.matches(path):
                return artifact_driver

        raise NeptuneUnhandledArtifactSchemeException(path)

    @classmethod
    def match_type(cls, type_str: str) -> type[ArtifactDriver]:
        for artifact_driver in cls._implementations:
            if artifact_driver.get_type() == type_str:
                return artifact_driver

        raise NeptuneUnhandledArtifactTypeException(type_str)


class ArtifactDriver(abc.ABC):
    def __init_subclass__(cls):
        ArtifactDriversMap._implementations.append(cls)

    @staticmethod
    def get_type() -> str:
        raise NotImplementedError

    @classmethod
    def matches(cls, path: str) -> bool:
        raise NotImplementedError

    @classmethod
    def get_tracked_files(cls, path: str, destination: str | None = None) -> list[ArtifactFileData]:
        raise NotImplementedError

    @classmethod
    def download_file(cls, destination: pathlib.Path, file_definition: ArtifactFileData):
        raise NotImplementedError
