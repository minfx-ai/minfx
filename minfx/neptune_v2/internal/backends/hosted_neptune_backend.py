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

from typing import Any

__all__ = ["HostedNeptuneBackend"]

import itertools
import os
import re
from typing import (
    TYPE_CHECKING,
    Generator,
    Iterable,
)
from urllib.parse import urlparse

# Minfx base URLs for non-neptune.ai backends
MINFX_APP_URL = "https://app.minfx.ai"
MINFX_DEMO_URL = "https://demo.minfx.ai"
MINFX_URL_LOCAL = "http://localhost:5000"

from bravado.exception import (
    HTTPConflict,
    HTTPNotFound,
    HTTPPaymentRequired,
    HTTPUnprocessableEntity,
)

from minfx.neptune_v2.api.dtos import FileEntry
from minfx.neptune_v2.api.searching_entries import iter_over_pages
from minfx.neptune_v2.common.backends.utils import with_api_exceptions_handler
from minfx.neptune_v2.common.exceptions import (
    ClientHttpError,
    InternalClientError,
    NeptuneException,
)
from minfx.neptune_v2.common.patterns import PROJECT_QUALIFIED_NAME_PATTERN
from minfx.neptune_v2.common.warnings import (
    NeptuneWarning,
    warn_once,
)
from minfx.neptune_v2.envs import NEPTUNE_FETCH_TABLE_STEP_SIZE
from minfx.neptune_v2.exceptions import (
    AmbiguousProjectName,
    ContainerUUIDNotFound,
    FetchAttributeNotFoundException,
    FileSetNotFound,
    MetadataContainerNotFound,
    MetadataInconsistency,
    NeptuneFeatureNotAvailableException,
    NeptuneLegacyProjectException,
    NeptuneLimitExceedException,
    NeptuneObjectCreationConflict,
    ProjectNotFound,
    ProjectNotFoundWithSuggestions,
)
from minfx.neptune_v2.internal.backends.api_model import (
    ApiExperiment,
    ArtifactAttribute,
    Attribute,
    AttributeType,
    BoolAttribute,
    DatetimeAttribute,
    FileAttribute,
    FloatAttribute,
    FloatPointValue,
    FloatSeriesAttribute,
    FloatSeriesValues,
    ImageSeriesValues,
    IntAttribute,
    LeaderboardEntry,
    OptionalFeatures,
    Project,
    StringAttribute,
    StringPointValue,
    StringSeriesAttribute,
    StringSeriesValues,
    StringSetAttribute,
    Workspace,
)
from minfx.neptune_v2.internal.backends.hosted_artifact_operations import (
    get_artifact_attribute,
    list_artifact_files,
    track_to_existing_artifact,
    track_to_new_artifact,
)
from minfx.neptune_v2.internal.backends.hosted_client import (
    DEFAULT_REQUEST_KWARGS,
    create_artifacts_client,
    create_backend_client,
    create_http_client_with_auth,
    create_leaderboard_client,
)
from minfx.neptune_v2.internal.backends.hosted_file_operations import (
    download_file_attribute,
    download_file_set_attribute,
    download_image_series_element,
    upload_file_attribute,
    upload_file_set_attribute,
)
from minfx.neptune_v2.internal.backends.neptune_backend import NeptuneBackend
from minfx.neptune_v2.internal.backends.operation_api_name_visitor import OperationApiNameVisitor
from minfx.neptune_v2.internal.backends.operation_api_object_converter import OperationApiObjectConverter
from minfx.neptune_v2.internal.backends.operations_preprocessor import OperationsPreprocessor
from minfx.neptune_v2.internal.backends.utils import (
    ExecuteOperationsBatchingManager,
    MissingApiClient,
    build_operation_url,
    ssl_verify,
)
from minfx.neptune_v2.internal.container_type import ContainerType
from minfx.neptune_v2.internal.operation import (
    DeleteAttribute,
    Operation,
    TrackFilesToArtifact,
    UploadFile,
    UploadFileContent,
    UploadFileSet,
)
from minfx.neptune_v2.internal.utils import base64_decode
from minfx.neptune_v2.internal.utils.generic_attribute_mapper import map_attribute_result_to_value
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.paths import path_to_str
from minfx.neptune_v2.internal.websockets.websockets_factory import WebsocketsFactory
from minfx.neptune_v2.management.exceptions import ObjectNotFound
from minfx.neptune_v2.version import version as neptune_client_version

if TYPE_CHECKING:
    from bravado.requests_client import RequestsClient

    from minfx.neptune_v2.core.components.operation_storage import OperationStorage
    from minfx.neptune_v2.internal.artifacts.types import ArtifactFileData
    from minfx.neptune_v2.internal.backends.api_model import ClientConfig
    from minfx.neptune_v2.internal.backends.nql import NQLQuery
    from minfx.neptune_v2.internal.credentials import Credentials
    from minfx.neptune_v2.internal.id_formats import (
        QualifiedName,
        UniqueId,
    )
    from minfx.neptune_v2.internal.utils.git import GitInfo
    from minfx.neptune_v2.typing import ProgressBarType


_logger = get_logger()

ATOMIC_ATTRIBUTE_TYPES = {
    AttributeType.INT.value,
    AttributeType.FLOAT.value,
    AttributeType.STRING.value,
    AttributeType.BOOL.value,
    AttributeType.DATETIME.value,
    AttributeType.RUN_STATE.value,
}

ATOMIC_ATTRIBUTE_TYPES = {
    AttributeType.INT.value,
    AttributeType.FLOAT.value,
    AttributeType.STRING.value,
    AttributeType.BOOL.value,
    AttributeType.DATETIME.value,
    AttributeType.RUN_STATE.value,
}


class HostedNeptuneBackend(NeptuneBackend):
    def __init__(
        self,
        credentials: Credentials,
        proxies: dict[str, str] | None = None,
        project_name_override: str | None = None,
        backend_index: int | None = None,
    ):
        # Set backend_index FIRST so retry handler can use it during initialization
        self.backend_index: int | None = backend_index

        self.credentials = credentials
        self.proxies = proxies
        self.missing_features = []
        self._project_name_override: str | None = project_name_override
        self._project_id_override: UniqueId | None = None  # Lazily resolved

        http_client, client_config, api_url = create_http_client_with_auth(
            credentials=credentials,
            ssl_verify=ssl_verify(),
            proxies=proxies,
            backend_index=backend_index,
        )
        self._http_client: RequestsClient = http_client
        self._client_config: ClientConfig = client_config
        self._api_url: str = api_url  # Token's api_url - single source of truth

        self.backend_client = create_backend_client(self._api_url, self._http_client)
        self.leaderboard_client = create_leaderboard_client(self._api_url, self._http_client)

        if self._client_config.has_feature(OptionalFeatures.ARTIFACTS):
            self.artifacts_client = create_artifacts_client(self._api_url, self._http_client)
        else:
            # create a stub
            self.artifacts_client = MissingApiClient(OptionalFeatures.ARTIFACTS)

        self.sys_name_set_by_backend = self._client_config.sys_name_set_by_backend

        # Container workspace mapping for minfx org lookup optimization
        self._container_workspaces: dict[str, str] = {}  # container_id → workspace

    def set_container_workspace(self, container_id: str, workspace: str) -> None:
        """Store workspace for a container (used for minfx org lookup optimization)."""
        self._container_workspaces[container_id] = workspace

    def clear_container_workspace(self, container_id: str) -> None:
        """Remove workspace mapping for a container (called on close to prevent memory leak)."""
        self._container_workspaces.pop(container_id, None)

    def verify_feature_available(self, feature_name: str):
        if not self._client_config.has_feature(feature_name):
            raise NeptuneFeatureNotAvailableException(feature_name)

    def get_display_address(self) -> str:
        # Use token's api_url, not server's applicationUrl response
        # This ensures links match the backend the client actually connected to
        return self._api_url

    def get_effective_project_id(self, default_project_id: UniqueId) -> UniqueId:
        """Returns the effective project_id for this backend.

        If a project_name_override was specified during creation and hasn't been
        resolved yet, this method lazily resolves it to a project_id.

        Args:
            default_project_id: The project_id to use if no override is set.

        Returns:
            The backend's project_id override if set, otherwise the default_project_id.
        """
        if self._project_name_override is None:
            return default_project_id

        # Lazy resolution of project name to project_id
        if self._project_id_override is None:
            project = self.get_project(self._project_name_override)
            self._project_id_override = project.id

        return self._project_id_override

    def has_project_override(self) -> bool:
        """Returns True if this backend has a project override configured."""
        return self._project_name_override is not None

    def websockets_factory(self, project_id: str, run_id: str) -> WebsocketsFactory | None:
        base_url = re.sub(r"^http", "ws", self._api_url)
        return WebsocketsFactory(
            url=build_operation_url(base_url, f"/api/notifications/v1/runs/{project_id}/{run_id}/signal"),
            session=self._http_client.authenticator.auth.session,
            proxies=self.proxies,
        )

    @with_api_exceptions_handler
    def get_project(self, project_id: QualifiedName) -> Project:
        project_spec = re.search(PROJECT_QUALIFIED_NAME_PATTERN, project_id)
        workspace, name = project_spec["workspace"], project_spec["project"]

        try:
            if not workspace:
                available_projects = list(
                    filter(
                        lambda p: p.name == name,
                        self.get_available_projects(search_term=name),
                    )
                )

                if len(available_projects) == 1:
                    project = available_projects[0]
                    project_id = f"{project.workspace}/{project.name}"
                elif len(available_projects) > 1:
                    raise AmbiguousProjectName(project_id=project_id, available_projects=available_projects)
                else:
                    raise ProjectNotFoundWithSuggestions(
                        project_id=project_id,
                        available_projects=self.get_available_projects(),
                        available_workspaces=self.get_available_workspaces(),
                    )

            response = self.backend_client.api.getProject(
                projectIdentifier=project_id,
                **DEFAULT_REQUEST_KWARGS,
            ).response()
            project = response.result
            project_version = project.version if hasattr(project, "version") else 1
            if project_version < 2:
                raise NeptuneLegacyProjectException(project_id)
            return Project(
                id=project.id,
                name=project.name,
                workspace=project.organizationName,
                sys_id=project.projectKey,
            )
        except HTTPNotFound:
            available_workspaces = self.get_available_workspaces()

            if workspace and not list(filter(lambda aw: aw.name == workspace, available_workspaces)):
                # Could not found specified workspace, forces listing all projects
                raise ProjectNotFoundWithSuggestions(
                    project_id=project_id,
                    available_projects=self.get_available_projects(),
                    available_workspaces=available_workspaces,
                )
            raise ProjectNotFoundWithSuggestions(
                project_id=project_id,
                available_projects=self.get_available_projects(workspace_id=workspace),
            )

    @with_api_exceptions_handler
    def get_available_projects(self, workspace_id: str | None = None, search_term: str | None = None) -> list[Project]:
        try:
            response = self.backend_client.api.listProjects(
                limit=5,
                organizationIdentifier=workspace_id,
                searchTerm=search_term,
                sortBy=["lastViewed"],
                sortDirection=["descending"],
                userRelation="memberOrHigher",
                **DEFAULT_REQUEST_KWARGS,
            ).response()
            projects = response.result.entries
            return [
                Project(
                    id=project.id,
                    name=project.name,
                    workspace=project.organizationName,
                    sys_id=project.projectKey,
                )
                for project in projects
            ]
        except HTTPNotFound:
            return []

    @with_api_exceptions_handler
    def get_available_workspaces(self) -> list[Workspace]:
        try:
            response = self.backend_client.api.listOrganizations(
                **DEFAULT_REQUEST_KWARGS,
            ).response()
            workspaces = response.result
            return [Workspace(id=workspace.id, name=workspace.name) for workspace in workspaces]
        except HTTPNotFound:
            return []

    @with_api_exceptions_handler
    def get_metadata_container(
        self,
        container_id: UniqueId | QualifiedName,
        expected_container_type: ContainerType | None,
    ) -> ApiExperiment:
        try:
            experiment = (
                self.leaderboard_client.api.getExperiment(
                    experimentId=container_id,
                    **DEFAULT_REQUEST_KWARGS,
                )
                .response()
                .result
            )

            if (
                expected_container_type is not None
                and ContainerType.from_api(experiment.type) != expected_container_type
            ):
                raise MetadataContainerNotFound.of_container_type(
                    container_type=expected_container_type, container_id=container_id
                )

            return ApiExperiment.from_experiment(experiment)
        except ObjectNotFound:
            raise MetadataContainerNotFound.of_container_type(
                container_type=expected_container_type, container_id=container_id
            )

    @with_api_exceptions_handler
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
        # Use effective project_id (allows per-backend project override)
        effective_project_id = self.get_effective_project_id(project_id)

        git_info_serialized = (
            {
                "commit": {
                    "commitId": git_info.commit_id,
                    "message": git_info.message,
                    "authorName": git_info.author_name,
                    "authorEmail": git_info.author_email,
                    "commitDate": git_info.commit_date,
                },
                "repositoryDirty": git_info.dirty,
                "currentBranch": git_info.branch,
                "remotes": git_info.remotes,
            }
            if git_info
            else None
        )

        additional_params = {
            "gitInfo": git_info_serialized,
            "customId": custom_run_id,
        }

        # Internal params for multi-backend ID synchronization (Minato backends only)
        # Neptune Labs will ignore these unknown fields
        if _external_id is not None:
            additional_params["_externalId"] = _external_id
        if _external_sys_id is not None:
            additional_params["_externalSysId"] = _external_sys_id

        if notebook_id is not None and checkpoint_id is not None:
            additional_params["notebookId"] = notebook_id if notebook_id is not None else None
            additional_params["checkpointId"] = checkpoint_id if checkpoint_id is not None else None

        return self._create_experiment(
            project_id=effective_project_id,
            parent_id=effective_project_id,
            container_type=ContainerType.RUN,
            additional_params=additional_params,
        )

    @with_api_exceptions_handler
    def create_model(self, project_id: UniqueId, key: str = "") -> ApiExperiment:
        # Use effective project_id (allows per-backend project override)
        effective_project_id = self.get_effective_project_id(project_id)

        additional_params = {
            "key": key,
        }

        return self._create_experiment(
            project_id=effective_project_id,
            parent_id=effective_project_id,
            container_type=ContainerType.MODEL,
            additional_params=additional_params,
        )

    @with_api_exceptions_handler
    def create_model_version(self, project_id: UniqueId, model_id: UniqueId) -> ApiExperiment:
        # Use effective project_id (allows per-backend project override)
        effective_project_id = self.get_effective_project_id(project_id)

        return self._create_experiment(
            project_id=effective_project_id,
            parent_id=model_id,
            container_type=ContainerType.MODEL_VERSION,
        )

    def _create_experiment(
        self,
        project_id: UniqueId,
        parent_id: UniqueId,
        container_type: ContainerType,
        additional_params: dict | None = None,
    ) -> ApiExperiment:
        if additional_params is None:
            additional_params = {}

        params = {
            "projectIdentifier": project_id,
            "parentId": parent_id,
            "type": container_type.to_api(),
            "cliVersion": str(neptune_client_version),
            **additional_params,
        }

        kwargs = {
            "experimentCreationParams": params,
            "X-Neptune-CliVersion": str(neptune_client_version),
            **DEFAULT_REQUEST_KWARGS,
        }

        try:
            experiment = self.leaderboard_client.api.createExperiment(**kwargs).response().result
            api_experiment = ApiExperiment.from_experiment(experiment)

            # Auto-register this backend's workspace for the created container.
            # This ensures multi-backend setups use the correct per-backend workspace
            # for org lookup optimization (each backend may have different projects).
            self.set_container_workspace(api_experiment.id, api_experiment.workspace)

            return api_experiment
        except HTTPNotFound:
            raise ProjectNotFound(project_id=project_id)
        except HTTPConflict as e:
            raise NeptuneObjectCreationConflict from e

    @with_api_exceptions_handler
    def create_checkpoint(self, notebook_id: str, jupyter_path: str) -> str | None:
        try:
            return (
                self.leaderboard_client.api.createEmptyCheckpoint(
                    notebookId=notebook_id,
                    checkpoint={"path": jupyter_path},
                    **DEFAULT_REQUEST_KWARGS,
                )
                .response()
                .result.id
            )
        except HTTPNotFound:
            return None

    @with_api_exceptions_handler
    def ping(self, container_id: str, container_type: ContainerType):
        request_kwargs = {
            "_request_options": {
                "timeout": 10,
                "connect_timeout": 10,
            }
        }
        try:
            self.leaderboard_client.api.ping(
                experimentId=container_id,
                **request_kwargs,
            ).response().result
        except HTTPNotFound as e:
            raise ContainerUUIDNotFound(container_id, container_type) from e

    @with_api_exceptions_handler
    def health_ping(self) -> None:
        """Health check via lightweight API call.

        Uses the backend client's version endpoint which is fast and doesn't
        require any specific container to exist.
        """
        request_kwargs = {
            "_request_options": {
                "timeout": 5,
                "connect_timeout": 5,
            }
        }
        self.backend_client.api.getClientConfig(**request_kwargs).response()

    def execute_operations(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        operations: list[Operation],
        operation_storage: OperationStorage,
    ) -> tuple[int, list[NeptuneException]]:
        errors = []

        batching_mgr = ExecuteOperationsBatchingManager(self)
        operations_batch = batching_mgr.get_batch(operations)
        errors.extend(operations_batch.errors)
        dropped_count = operations_batch.dropped_operations_count

        operations_preprocessor = OperationsPreprocessor()
        operations_preprocessor.process(operations_batch.operations)

        preprocessed_operations = operations_preprocessor.get_operations()
        errors.extend(preprocessed_operations.errors)

        if preprocessed_operations.artifact_operations:
            self.verify_feature_available(OptionalFeatures.ARTIFACTS)

        # Upload operations should be done first since they are idempotent
        errors.extend(
            self._execute_upload_operations_with_400_retry(
                container_id=container_id,
                container_type=container_type,
                upload_operations=preprocessed_operations.upload_operations,
                operation_storage=operation_storage,
            )
        )

        (
            artifact_operations_errors,
            assign_artifact_operations,
        ) = self._execute_artifact_operations(
            container_id=container_id,
            container_type=container_type,
            artifact_operations=preprocessed_operations.artifact_operations,
        )

        errors.extend(artifact_operations_errors)

        errors.extend(
            self._execute_operations(
                container_id,
                container_type,
                operations=assign_artifact_operations + preprocessed_operations.other_operations,
            )
        )

        for op in itertools.chain(
            preprocessed_operations.upload_operations,
            assign_artifact_operations,
            preprocessed_operations.other_operations,
        ):
            op.clean(operation_storage=operation_storage)

        return (
            operations_preprocessor.processed_ops_count + dropped_count,
            errors,
        )

    def _execute_upload_operations(
        self,
        container_id: str,
        container_type: ContainerType,
        upload_operations: list[Operation],
        operation_storage: OperationStorage,
    ) -> list[NeptuneException]:
        errors = []

        if self._client_config.has_feature(OptionalFeatures.MULTIPART_UPLOAD):
            multipart_config = self._client_config.multipart_config
            # collect delete operations and execute them
            attributes_to_reset = [
                DeleteAttribute(op.path) for op in upload_operations if isinstance(op, UploadFileSet) and op.reset
            ]
            if attributes_to_reset:
                errors.extend(self._execute_operations(container_id, container_type, operations=attributes_to_reset))
        else:
            multipart_config = None

        for op in upload_operations:
            if isinstance(op, UploadFile):
                upload_errors = upload_file_attribute(
                    swagger_client=self.leaderboard_client,
                    container_id=container_id,
                    attribute=path_to_str(op.path),
                    source=op.get_absolute_path(operation_storage),
                    ext=op.ext,
                    multipart_config=multipart_config,
                )
                if upload_errors:
                    errors.extend(upload_errors)
            elif isinstance(op, UploadFileContent):
                upload_errors = upload_file_attribute(
                    swagger_client=self.leaderboard_client,
                    container_id=container_id,
                    attribute=path_to_str(op.path),
                    source=base64_decode(op.file_content),
                    ext=op.ext,
                    multipart_config=multipart_config,
                )
                if upload_errors:
                    errors.extend(upload_errors)
            elif isinstance(op, UploadFileSet):
                upload_errors = upload_file_set_attribute(
                    swagger_client=self.leaderboard_client,
                    container_id=container_id,
                    attribute=path_to_str(op.path),
                    file_globs=op.file_globs,
                    reset=op.reset,
                    multipart_config=multipart_config,
                )
                if upload_errors:
                    errors.extend(upload_errors)
            else:
                raise InternalClientError("Upload operation in neither File or FileSet")

        return errors

    def _execute_upload_operations_with_400_retry(
        self,
        container_id: str,
        container_type: ContainerType,
        upload_operations: list[Operation],
        operation_storage: OperationStorage,
    ) -> list[NeptuneException]:
        while True:
            try:
                return self._execute_upload_operations(
                    container_id, container_type, upload_operations, operation_storage
                )
            except ClientHttpError as ex:
                if "Length of stream does not match given range" not in ex.response:
                    raise

    @with_api_exceptions_handler
    def _execute_artifact_operations(
        self,
        container_id: str,
        container_type: ContainerType,
        artifact_operations: list[TrackFilesToArtifact],
    ) -> tuple[list[NeptuneException | None], list[Operation | None]]:
        errors = []
        assign_operations = []

        has_hash_exclude_metadata = self._client_config.has_feature(OptionalFeatures.ARTIFACTS_HASH_EXCLUDE_METADATA)
        has_exclude_directories = self._client_config.has_feature(OptionalFeatures.ARTIFACTS_EXCLUDE_DIRECTORY_FILES)

        for op in artifact_operations:
            try:
                artifact_hash = self.get_artifact_attribute(container_id, container_type, op.path).hash
            except FetchAttributeNotFoundException:
                artifact_hash = None

            try:
                if artifact_hash is None:
                    assign_operation = track_to_new_artifact(
                        swagger_client=self.artifacts_client,
                        project_id=op.project_id,
                        path=op.path,
                        parent_identifier=container_id,
                        entries=op.entries,
                        default_request_params=DEFAULT_REQUEST_KWARGS,
                        exclude_directory_files=has_exclude_directories,
                        exclude_metadata_from_hash=has_hash_exclude_metadata,
                    )
                else:
                    assign_operation = track_to_existing_artifact(
                        swagger_client=self.artifacts_client,
                        project_id=op.project_id,
                        path=op.path,
                        artifact_hash=artifact_hash,
                        parent_identifier=container_id,
                        entries=op.entries,
                        default_request_params=DEFAULT_REQUEST_KWARGS,
                        exclude_directory_files=has_exclude_directories,
                    )

                if assign_operation:
                    assign_operations.append(assign_operation)
            except NeptuneException as error:
                errors.append(error)

        return errors, assign_operations

    @with_api_exceptions_handler
    def _execute_operations(
        self,
        container_id: UniqueId,
        container_type: ContainerType,
        operations: list[Operation],
    ) -> list[MetadataInconsistency]:
        kwargs = {
            "experimentId": container_id,
            "operations": [
                {
                    "path": path_to_str(op.path),
                    OperationApiNameVisitor().visit(op): OperationApiObjectConverter().convert(op),
                }
                for op in operations
            ],
            **DEFAULT_REQUEST_KWARGS,
        }

        # Add organizationName for minfx backends (optimization for org lookup)
        if not self._is_neptune_ai_backend():
            workspace = self._container_workspaces.get(container_id)
            if workspace:
                kwargs["organizationName"] = workspace

        try:
            result = self.leaderboard_client.api.executeOperations(**kwargs).response().result
            return [MetadataInconsistency(err.errorDescription) for err in result]
        except HTTPNotFound as e:
            raise ContainerUUIDNotFound(container_id, container_type) from e
        except (HTTPPaymentRequired, HTTPUnprocessableEntity) as e:
            raise NeptuneLimitExceedException(reason=e.response.json().get("title", "Unknown reason")) from e

    @with_api_exceptions_handler
    def get_attributes(self, container_id: str, container_type: ContainerType) -> list[Attribute]:
        def to_attribute(attr: object) -> Attribute:
            return Attribute(attr.name, AttributeType(attr.type))

        params = {
            "experimentId": container_id,
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            experiment = self.leaderboard_client.api.getExperimentAttributes(**params).response().result

            attribute_type_names = [at.value for at in AttributeType]
            accepted_attributes = [attr for attr in experiment.attributes if attr.type in attribute_type_names]

            # Notify about ignored attrs
            ignored_attributes = {attr.type for attr in experiment.attributes} - {
                attr.type for attr in accepted_attributes
            }
            if ignored_attributes:
                _logger.warning(
                    "Ignored following attributes (unknown type): %s.\nTry to upgrade `neptune`.",
                    ignored_attributes,
                )

            return [to_attribute(attr) for attr in accepted_attributes if attr.type in attribute_type_names]
        except HTTPNotFound as e:
            raise ContainerUUIDNotFound(
                container_id=container_id,
                container_type=container_type,
            ) from e

    def download_file_series_by_index(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        index: int,
        destination: str,
        progress_bar: ProgressBarType | None,
    ):
        try:
            download_image_series_element(
                swagger_client=self.leaderboard_client,
                container_id=container_id,
                attribute=path_to_str(path),
                index=index,
                destination=destination,
                progress_bar=progress_bar,
            )
        except ClientHttpError as e:
            if e.status == HTTPNotFound.status_code:
                raise FetchAttributeNotFoundException(path_to_str(path))
            raise

    def download_file(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        destination: str | None = None,
        progress_bar: ProgressBarType | None = None,
    ):
        try:
            download_file_attribute(
                swagger_client=self.leaderboard_client,
                container_id=container_id,
                attribute=path_to_str(path),
                destination=destination,
                progress_bar=progress_bar,
            )
        except ClientHttpError as e:
            if e.status == HTTPNotFound.status_code:
                raise FetchAttributeNotFoundException(path_to_str(path))
            raise

    def download_file_set(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        destination: str | None = None,
        progress_bar: ProgressBarType | None = None,
    ):
        download_request = self._get_file_set_download_request(container_id, container_type, path)
        try:
            download_file_set_attribute(
                swagger_client=self.leaderboard_client,
                download_id=download_request.id,
                destination=destination,
                progress_bar=progress_bar,
            )
        except ClientHttpError as e:
            if e.status == HTTPNotFound.status_code:
                raise FetchAttributeNotFoundException(path_to_str(path))
            raise

    @with_api_exceptions_handler
    def get_float_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> FloatAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getFloatAttribute(**params).response().result
            return FloatAttribute(result.value)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_int_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> IntAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getIntAttribute(**params).response().result
            return IntAttribute(result.value)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_bool_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> BoolAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getBoolAttribute(**params).response().result
            return BoolAttribute(result.value)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_file_attribute(self, container_id: str, container_type: ContainerType, path: list[str]) -> FileAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getFileAttribute(**params).response().result
            return FileAttribute(name=result.name, ext=result.ext, size=result.size)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_string_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getStringAttribute(**params).response().result
            return StringAttribute(result.value)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_datetime_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> DatetimeAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getDatetimeAttribute(**params).response().result
            return DatetimeAttribute(result.value)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    def get_artifact_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> ArtifactAttribute:
        return get_artifact_attribute(
            swagger_client=self.leaderboard_client,
            parent_identifier=container_id,
            path=path,
            default_request_params=DEFAULT_REQUEST_KWARGS,
        )

    def list_artifact_files(self, project_id: str, artifact_hash: str) -> list[ArtifactFileData]:
        return list_artifact_files(
            swagger_client=self.artifacts_client,
            project_id=project_id,
            artifact_hash=artifact_hash,
            default_request_params=DEFAULT_REQUEST_KWARGS,
        )

    @with_api_exceptions_handler
    def list_fileset_files(self, attribute: list[str], container_id: str, path: str) -> list[FileEntry]:
        attribute = path_to_str(attribute)
        try:
            entries = (
                self.leaderboard_client.api.lsFileSetAttribute(
                    attribute=attribute, path=path, experimentId=container_id, **DEFAULT_REQUEST_KWARGS
                )
                .response()
                .result
            )
            return [FileEntry.from_dto(entry) for entry in entries]
        except HTTPNotFound:
            raise FileSetNotFound(attribute, path)

    @with_api_exceptions_handler
    def get_float_series_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> FloatSeriesAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getFloatSeriesAttribute(**params).response().result
            return FloatSeriesAttribute(result.last)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_string_series_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringSeriesAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getStringSeriesAttribute(**params).response().result
            return StringSeriesAttribute(result.last)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_string_set_attribute(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> StringSetAttribute:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getStringSetAttribute(**params).response().result
            return StringSetAttribute(set(result.values))
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_image_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> ImageSeriesValues:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            "limit": limit,
            "offset": offset,
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getImageSeriesValues(**params).response().result
            return ImageSeriesValues(result.totalItemCount)
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_string_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> StringSeriesValues:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            "limit": limit,
            "offset": offset,
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getStringSeriesValues(**params).response().result
            return StringSeriesValues(
                result.totalItemCount,
                [StringPointValue(v.timestampMillis, v.step, v.value) for v in result.values],
            )
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def get_float_series_values(
        self,
        container_id: str,
        container_type: ContainerType,
        path: list[str],
        offset: int,
        limit: int,
    ) -> FloatSeriesValues:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            "limit": limit,
            "offset": offset,
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            result = self.leaderboard_client.api.getFloatSeriesValues(**params).response().result
            return FloatSeriesValues(
                result.totalItemCount,
                [FloatPointValue(v.timestampMillis, v.step, v.value) for v in result.values],
            )
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def fetch_atom_attribute_values(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> list[tuple[str, AttributeType, Any]]:
        params = {
            "experimentId": container_id,
        }
        try:
            namespace_prefix = path_to_str(path)
            if namespace_prefix:
                # don't want to catch "ns/attribute/other" while looking for "ns/attr"
                namespace_prefix += "/"
            result = self.leaderboard_client.api.getExperimentAttributes(**params).response().result
            return [
                (attr.name, attr.type, map_attribute_result_to_value(attr))
                for attr in result.attributes
                if attr.name.startswith(namespace_prefix)
            ]
        except HTTPNotFound as e:
            raise ContainerUUIDNotFound(container_id, container_type) from e

    @with_api_exceptions_handler
    def _get_file_set_download_request(
        self, container_id: str, container_type: ContainerType, path: list[str]
    ) -> object:
        params = {
            "experimentId": container_id,
            "attribute": path_to_str(path),
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            return self.leaderboard_client.api.prepareForDownloadFileSetAttributeZip(**params).response().result
        except HTTPNotFound:
            raise FetchAttributeNotFoundException(path_to_str(path))

    @with_api_exceptions_handler
    def _get_column_types(self, project_id: UniqueId, column: str, types: Iterable[str] | None = None) -> list[Any]:
        params = {
            "projectIdentifier": project_id,
            "search": column,
            "type": types,
            "params": {},
            **DEFAULT_REQUEST_KWARGS,
        }
        try:
            return self.leaderboard_client.api.searchLeaderboardAttributes(**params).response().result.entries
        except HTTPNotFound as e:
            raise ProjectNotFound(project_id=project_id) from e

    @with_api_exceptions_handler
    def search_leaderboard_entries(
        self,
        project_id: UniqueId,
        types: Iterable[ContainerType] | None = None,
        query: NQLQuery | None = None,
        columns: Iterable[str] | None = None,
        limit: int | None = None,
        sort_by: str = "sys/creation_time",
        ascending: bool = False,
        progress_bar: ProgressBarType | None = None,
        step_size: int | None = None,
    ) -> Generator[LeaderboardEntry, None, None]:
        default_step_size = step_size or int(os.getenv(NEPTUNE_FETCH_TABLE_STEP_SIZE, "100"))

        step_size = min(default_step_size, limit) if limit else default_step_size

        types_filter = [container_type.to_api() for container_type in types] if types else None
        attributes_filter = {"attributeFilters": [{"path": column} for column in columns]} if columns else {}

        if sort_by == "sys/creation_time":
            sort_by_column_type = AttributeType.DATETIME.value
        if sort_by == "sys/id":
            sort_by_column_type = AttributeType.STRING.value
        else:
            sort_by_column_type_candidates = self._get_column_types(project_id, sort_by, types_filter)
            sort_by_column_type = _get_column_type_from_entries(sort_by_column_type_candidates, sort_by)

        try:
            return iter_over_pages(
                client=self.leaderboard_client,
                project_id=project_id,
                types=types_filter,
                query=query,
                attributes_filter=attributes_filter,
                step_size=step_size,
                limit=limit,
                sort_by=sort_by,
                ascending=ascending,
                sort_by_column_type=sort_by_column_type,
                progress_bar=progress_bar,
            )
        except HTTPNotFound:
            raise ProjectNotFound(project_id)

    def _is_neptune_ai_backend(self) -> bool:
        """Check if this backend is the official neptune.ai service."""
        base_url = self.get_display_address()
        return "neptune.ai" in base_url

    def _get_minfx_frontend_url(self) -> str:
        """Determine the minfx frontend URL based on backend URL.

        Detects flavor from API URL:
        - If URL contains 'demo.' (e.g., demo.neptune2.minfx.ai or demo.neptune2.localhost)
          → use demo frontend URL
        - Otherwise → use app frontend URL

        Also handles local development URLs with ports.
        """
        base_url = self.get_display_address()
        parsed = urlparse(base_url)
        host = parsed.netloc.lower()

        # Check if this is a demo flavor backend
        is_demo_flavor = "demo." in host
        is_localhost = "localhost" in host

        if is_localhost:
            return MINFX_URL_LOCAL

        if is_demo_flavor:
            return MINFX_DEMO_URL
        else:
            return MINFX_APP_URL

    def _get_minfx_link(self, workspace: str, project_name: str, sys_id: str) -> str:
        """Generate minfx.ai link for non-neptune.ai backends.

        Format: {frontend_url}/#link:{workspace}/{project}/{sys_id}

        The frontend URL is dynamically determined based on the backend URL flavor.
        The backend host is not included - the frontend uses its compiled-in backend URL.
        """
        frontend_url = self._get_minfx_frontend_url()
        return f"{frontend_url}/#link:{workspace}/{project_name}/{sys_id}"

    def get_run_url(self, run_id: str, workspace: str, project_name: str, sys_id: str) -> str:
        if self._is_neptune_ai_backend():
            base_url = self.get_display_address()
            return f"{base_url}/{workspace}/{project_name}/e/{sys_id}"
        return self._get_minfx_link(workspace, project_name, sys_id)

    def get_project_url(self, project_id: str, workspace: str, project_name: str) -> str:
        base_url = self.get_display_address()
        return f"{base_url}/{workspace}/{project_name}/"

    def get_model_url(self, model_id: str, workspace: str, project_name: str, sys_id: str) -> str:
        if self._is_neptune_ai_backend():
            base_url = self.get_display_address()
            return f"{base_url}/{workspace}/{project_name}/m/{sys_id}"
        return self._get_minfx_link(workspace, project_name, sys_id)

    def get_model_version_url(
        self,
        model_version_id: str,
        model_id: str,
        workspace: str,
        project_name: str,
        sys_id: str,
    ) -> str:
        if self._is_neptune_ai_backend():
            base_url = self.get_display_address()
            return f"{base_url}/{workspace}/{project_name}/m/{model_id}/v/{sys_id}"
        return self._get_minfx_link(workspace, project_name, sys_id)


def _get_column_type_from_entries(entries: list[Any], column: str) -> str:
    if not entries:  # column chosen is not present in the table
        raise ValueError(f"Column '{column}' chosen for sorting is not present in the table")

    if len(entries) == 1 and entries[0].name == column:
        return entries[0].type

    types = set()
    for entry in entries:
        if entry.name != column:  # caught by regex, but it's not this column
            continue
        if entry.type not in ATOMIC_ATTRIBUTE_TYPES:  # non-atomic type - no need to look further
            raise ValueError(
                f"Column {column} used for sorting is a complex type. For more, "
                f"see https://docs-legacy.neptune.ai/api/field_types/#simple-types"
            )
        types.add(entry.type)

    if types == {AttributeType.INT.value, AttributeType.FLOAT.value}:
        return AttributeType.FLOAT.value

    warn_once(
        f"Column {column} contains more than one simple data type. Sorting result might be inaccurate.",
        exception=NeptuneWarning,
    )
    return AttributeType.STRING.value
