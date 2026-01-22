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

__all__ = [
    "ApiExperiment",
    "ArtifactAttribute",
    "ArtifactModel",
    "Attribute",
    "AttributeProperties",
    "AttributeType",
    "AttributeWithProperties",
    "BoolAttribute",
    "ClientConfig",
    "DatetimeAttribute",
    "FileAttribute",
    "FloatAttribute",
    "FloatPointValue",
    "FloatSeriesAttribute",
    "FloatSeriesValues",
    "ImageSeriesValues",
    "IntAttribute",
    "LeaderboardEntry",
    "OptionalFeatures",
    "Project",
    "StringAttribute",
    "StringPointValue",
    "StringSeriesAttribute",
    "StringSeriesValues",
    "StringSetAttribute",
    "VersionInfo",
    "Workspace",
]

from dataclasses import dataclass
from enum import Enum
from typing import (
    TYPE_CHECKING,
    TypedDict,
)

from packaging import version

from minfx.neptune_v2.common.backends.api_model import MultipartConfig
from minfx.neptune_v2.internal.container_type import ContainerType

if TYPE_CHECKING:
    from datetime import datetime

    from minfx.neptune_v2.internal.id_formats import (
        SysId,
        UniqueId,
    )


@dataclass
class Project:
    id: UniqueId
    name: str
    workspace: str
    sys_id: SysId


@dataclass
class Workspace:
    id: UniqueId
    name: str


@dataclass
class ApiExperiment:
    id: UniqueId
    type: ContainerType
    sys_id: SysId
    workspace: str
    project_name: str
    trashed: bool = False

    @classmethod
    def from_experiment(cls, response_exp: object) -> ApiExperiment:
        return cls(
            id=response_exp.id,
            type=ContainerType.from_api(response_exp.type),
            sys_id=response_exp.shortId,
            workspace=response_exp.organizationName,
            project_name=response_exp.projectName,
            trashed=response_exp.trashed,
        )


class OptionalFeatures:
    VERSION_INFO = "version_info"
    ARTIFACTS = "artifacts"
    ARTIFACTS_HASH_EXCLUDE_METADATA = "artifacts_hash_exclude_metadata"
    ARTIFACTS_EXCLUDE_DIRECTORY_FILES = "artifact_exclude_directory_files"
    MULTIPART_UPLOAD = "multipart_upload"


@dataclass(frozen=True)
class VersionInfo:
    min_recommended: version.Version | None
    min_compatible: version.Version | None
    max_compatible: version.Version | None

    @staticmethod
    def build(
        min_recommended: str | None,
        min_compatible: str | None,
        max_compatible: str | None,
    ) -> VersionInfo:
        return VersionInfo(
            min_recommended=version.parse(min_recommended) if min_recommended else None,
            min_compatible=version.parse(min_compatible) if min_compatible else None,
            max_compatible=version.parse(max_compatible) if max_compatible else None,
        )


@dataclass(frozen=True)
class ClientConfig:
    display_url: str
    _missing_features: frozenset[str]
    version_info: VersionInfo
    multipart_config: MultipartConfig
    sys_name_set_by_backend: bool

    def has_feature(self, feature_name: str) -> bool:
        return feature_name not in self._missing_features

    @staticmethod
    def from_api_response(config: object) -> ClientConfig:
        missing_features = []

        version_info_obj = getattr(config, "pyLibVersions", None)
        if version_info_obj is None:
            missing_features.append(OptionalFeatures.VERSION_INFO)
            min_recommended = min_compatible = max_compatible = None
        else:
            min_recommended = getattr(version_info_obj, "minRecommendedVersion", None)
            min_compatible = getattr(version_info_obj, "minCompatibleVersion", None)
            max_compatible = getattr(version_info_obj, "maxCompatibleVersion", None)

        multipart_upload_config_obj = getattr(config, "multiPartUpload", None)
        has_multipart_upload = getattr(multipart_upload_config_obj, "enabled", False)
        if not has_multipart_upload:
            missing_features.append(OptionalFeatures.MULTIPART_UPLOAD)
            multipart_upload_config = None
        else:
            min_chunk_size = multipart_upload_config_obj.minChunkSize
            max_chunk_size = multipart_upload_config_obj.maxChunkSize
            max_chunk_count = multipart_upload_config_obj.maxChunkCount
            max_single_part_size = multipart_upload_config_obj.maxSinglePartSize
            multipart_upload_config = MultipartConfig(
                min_chunk_size, max_chunk_size, max_chunk_count, max_single_part_size
            )

        artifacts_config_obj = getattr(config, "artifacts", None)
        has_artifacts = getattr(artifacts_config_obj, "enabled", False)
        if not has_artifacts:
            missing_features.append(OptionalFeatures.ARTIFACTS)

        artifacts_api_version = getattr(artifacts_config_obj, "apiVersion", 1)
        if artifacts_api_version == 1:
            missing_features.append(OptionalFeatures.ARTIFACTS_HASH_EXCLUDE_METADATA)
            missing_features.append(OptionalFeatures.ARTIFACTS_EXCLUDE_DIRECTORY_FILES)

        sys_name_set_by_backend = getattr(config, "sysNameSetByBackend", False)

        return ClientConfig(
            display_url=config.applicationUrl,
            _missing_features=frozenset(missing_features),
            version_info=VersionInfo.build(min_recommended, min_compatible, max_compatible),
            multipart_config=multipart_upload_config,
            sys_name_set_by_backend=sys_name_set_by_backend,
        )


class AttributeType(Enum):
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    DATETIME = "datetime"
    FILE = "file"
    FILE_SET = "fileSet"
    FLOAT_SERIES = "floatSeries"
    STRING_SERIES = "stringSeries"
    IMAGE_SERIES = "imageSeries"
    STRING_SET = "stringSet"
    GIT_REF = "gitRef"
    RUN_STATE = "experimentState"
    NOTEBOOK_REF = "notebookRef"
    ARTIFACT = "artifact"


class AttributeProperties(TypedDict, total=False):
    """Properties for different attribute types.

    This is a union of all possible property keys across all attribute types.
    Not all keys are present for all attribute types.
    """

    # Common value properties (FLOAT, INT, BOOL, STRING, DATETIME, RUN_STATE)
    value: float | int | bool | str
    # Series properties (FLOAT_SERIES, STRING_SERIES)
    last: float | str | None
    # StringSet properties
    values: list[str]
    # GitRef properties
    commit: dict[str, str]
    # NotebookRef properties
    notebookName: str
    # Artifact properties
    hash: str


@dataclass
class Attribute:
    path: str
    type: AttributeType


@dataclass
class AttributeWithProperties:
    path: str
    type: AttributeType
    properties: AttributeProperties


@dataclass
class LeaderboardEntry:
    id: str
    attributes: list[AttributeWithProperties]


@dataclass
class StringPointValue:
    timestampMillis: int
    step: float
    value: str


@dataclass
class ImageSeriesValues:
    totalItemCount: int


@dataclass
class StringSeriesValues:
    totalItemCount: int
    values: list[StringPointValue]


@dataclass
class FloatPointValue:
    timestampMillis: int
    step: float
    value: float


@dataclass
class FloatSeriesValues:
    totalItemCount: int
    values: list[FloatPointValue]


@dataclass
class FloatAttribute:
    value: float


@dataclass
class IntAttribute:
    value: int


@dataclass
class BoolAttribute:
    value: bool


@dataclass
class FileAttribute:
    name: str
    ext: str
    size: int


@dataclass
class StringAttribute:
    value: str


@dataclass
class DatetimeAttribute:
    value: datetime


@dataclass
class ArtifactAttribute:
    hash: str


@dataclass
class ArtifactModel:
    received_metadata: bool
    hash: str
    size: int


@dataclass
class FloatSeriesAttribute:
    last: float | None


@dataclass
class StringSeriesAttribute:
    last: str | None


@dataclass
class StringSetAttribute:
    values: set[str]
