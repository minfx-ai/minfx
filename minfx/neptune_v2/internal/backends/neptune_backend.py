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

__all__ = ["NeptuneBackend"]

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
)

if TYPE_CHECKING:
    from minfx.neptune_v2.api.dtos import FileEntry
    from minfx.neptune_v2.common.exceptions import NeptuneException
    from minfx.neptune_v2.core.components.operation_storage import OperationStorage
    from minfx.neptune_v2.internal.artifacts.types import ArtifactFileData
    from minfx.neptune_v2.internal.backends.api_model import (
        ApiExperiment,
        ArtifactAttribute,
        Attribute,
        AttributeType,
        BoolAttribute,
        DatetimeAttribute,
        FileAttribute,
        FloatAttribute,
        FloatSeriesAttribute,
        FloatSeriesValues,
        ImageSeriesValues,
        IntAttribute,
        LeaderboardEntry,
        Project,
        StringAttribute,
        StringSeriesAttribute,
        StringSeriesValues,
        StringSetAttribute,
        Workspace,
    )
    from minfx.neptune_v2.internal.backends.nql import NQLQuery
    from minfx.neptune_v2.internal.container_type import ContainerType
    from minfx.neptune_v2.internal.id_formats import (
        QualifiedName,
        UniqueId,
    )
    from minfx.neptune_v2.internal.operation import Operation
    from minfx.neptune_v2.internal.utils.git import GitInfo
    from minfx.neptune_v2.internal.websockets.websockets_factory import WebsocketsFactory
    from minfx.neptune_v2.typing import ProgressBarType


class NeptuneBackend:
    def close(self) -> None:
        """No need for closing implementation."""

    @abc.abstractmethod
    def get_display_address(self) -> str:
        pass

    def verify_feature_available(self, _: str) -> None:
        """This method makes sense only for backends interacting with server;
        it makes sure that a feature is supported in the backend version client interacts with.
        """

    def websockets_factory(self, project_id: str, run_id: str) -> WebsocketsFactory | None:
        return None

    @abc.abstractmethod
    def get_project(self, project_id: QualifiedName) -> Project:
        pass

    @abc.abstractmethod
    def get_available_projects(self, workspace_id: str | None = None, search_term: str | None = None) -> list[Project]:
        pass

    @abc.abstractmethod
    def get_available_workspaces(self) -> list[Workspace]:
        pass

    @abc.abstractmethod
    def create_run(
        self,
        project_id: UniqueId,
        git_info: GitInfo | None = None,
        custom_run_id: str | None = None,
        notebook_id: str | None = None,
        checkpoint_id: str | None = None,
        *,
        _external_id: str | None = None,
        _external_sys_id: str | None = None,
    ) -> ApiExperiment:
        """Create a new run.

        Args:
            project_id: The project to create the run in
            git_info: Optional git repository information
            custom_run_id: Optional user-defined run ID for cross-backend resume
            notebook_id: Optional notebook ID
            checkpoint_id: Optional checkpoint ID
            _external_id: Internal use only - UUID from primary backend
            _external_sys_id: Internal use only - sys_id from primary backend

        Returns:
            ApiExperiment with the created run's metadata
        """
        pass

    @abc.abstractmethod
    def create_model(
        self,
        project_id: UniqueId,
        key: str,
    ) -> ApiExperiment:
        pass

    @abc.abstractmethod
    def create_model_version(
        self,
        project_id: UniqueId,
        model_id: UniqueId,
    ) -> ApiExperiment:
        pass

    @abc.abstractmethod
    def get_metadata_container(
        self,
        container_id: UniqueId | QualifiedName,
        expected_container_type: ContainerType | None,
    ) -> ApiExperiment:
        pass

    @abc.abstractmethod
    def create_checkpoint(self, notebook_id: str, jupyter_path: str) -> str | None:
        pass

    def ping(self, container_id: str, container_type: ContainerType):
        """Do nothing by default."""

    def health_ping(self) -> None:
        """Health check for the backend.

        Should be a lightweight operation that verifies the backend is reachable
        and responding. Used by MultiBackend to check if degraded backends have
        recovered.

        Raises:
            Exception: If the backend is not reachable or unhealthy.
        """
        # Default implementation does nothing - subclasses should override

    @abc.abstractmethod
    def execute_operations(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        operations: list[Operation],
        operation_storage: OperationStorage,
    ) -> tuple[int, list[NeptuneException]]:
        pass

    @abc.abstractmethod
    def get_attributes(self, container_id: str, container_type: ContainerType) -> list[Attribute]:
        pass

    @abc.abstractmethod
    def download_file(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        destination: str | None = None,
        progress_bar: ProgressBarType | None = None,
    ):
        pass

    @abc.abstractmethod
    def download_file_set(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        destination: str | None = None,
        progress_bar: ProgressBarType | None = None,
    ):
        pass

    @abc.abstractmethod
    def get_float_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> FloatAttribute:
        pass

    @abc.abstractmethod
    def get_int_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> IntAttribute:
        pass

    @abc.abstractmethod
    def get_bool_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> BoolAttribute:
        pass

    @abc.abstractmethod
    def get_file_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> FileAttribute:
        pass

    @abc.abstractmethod
    def get_string_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringAttribute:
        pass

    @abc.abstractmethod
    def get_datetime_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> DatetimeAttribute:
        pass

    @abc.abstractmethod
    def get_artifact_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> ArtifactAttribute:
        pass

    @abc.abstractmethod
    def list_artifact_files(self, project_id: str, artifact_hash: str) -> list[ArtifactFileData]:
        pass

    @abc.abstractmethod
    def get_float_series_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> FloatSeriesAttribute:
        pass

    @abc.abstractmethod
    def get_string_series_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringSeriesAttribute:
        pass

    @abc.abstractmethod
    def get_string_set_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringSetAttribute:
        pass

    @abc.abstractmethod
    def download_file_series_by_index(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        index: int,
        destination: str,
        progress_bar: ProgressBarType | None,
    ):
        pass

    @abc.abstractmethod
    def get_image_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> ImageSeriesValues:
        pass

    @abc.abstractmethod
    def get_string_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> StringSeriesValues:
        pass

    @abc.abstractmethod
    def get_float_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> FloatSeriesValues:
        pass

    @abc.abstractmethod
    def get_run_url(self, run_id: str, workspace: str, project_name: str, sys_id: str) -> str:
        pass

    @abc.abstractmethod
    def get_project_url(self, project_id: str, workspace: str, project_name: str) -> str:
        pass

    @abc.abstractmethod
    def get_model_url(self, model_id: str, workspace: str, project_name: str, sys_id: str) -> str:
        pass

    @abc.abstractmethod
    def get_model_version_url(
        self,
        model_version_id: str,
        model_id: str,
        workspace: str,
        project_name: str,
        sys_id: str,
    ) -> str:
        pass

    @abc.abstractmethod
    def fetch_atom_attribute_values(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> list[tuple[str, AttributeType, Any]]:
        pass

    @abc.abstractmethod
    def search_leaderboard_entries(
        self,
        project_id: UniqueId,
        types: list[ContainerType] | None = None,
        query: NQLQuery | None = None,
        columns: list[str] | None = None,
        limit: int | None = None,
        sort_by: str = "sys/creation_time",
        ascending: bool = False,
        progress_bar: ProgressBarType | None = None,
    ) -> Generator[LeaderboardEntry, None, None]:
        pass

    @abc.abstractmethod
    def list_fileset_files(self, attribute: list[str], container_id: str, path: str) -> list[FileEntry]:
        pass
