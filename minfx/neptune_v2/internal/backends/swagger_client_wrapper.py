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

__all__ = ["ApiMethodWrapper", "SwaggerClientWrapper"]

from typing import (
    TYPE_CHECKING,
)

from bravado.exception import HTTPError

from minfx.neptune_v2.api.requests_utils import ensure_json_response
from minfx.neptune_v2.common.exceptions import (
    NeptuneAuthTokenExpired,
    WritingToArchivedProjectException,
)
from minfx.neptune_v2.exceptions import (
    NeptuneFieldCountLimitExceedException,
    NeptuneLimitExceedException,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from bravado.client import SwaggerClient


from typing import Callable


class ApiMethodWrapper:
    def __init__(self, api_method: Callable[..., object]) -> None:
        self._api_method = api_method

    @staticmethod
    def handle_neptune_http_errors(response: object, exception: HTTPError | None = None) -> None:
        from minfx.neptune_v2.management.exceptions import (
            ActiveProjectsLimitReachedException,
            IncorrectIdentifierException,
            ObjectNotFound,
            ProjectKeyCollision,
            ProjectKeyInvalid,
            ProjectNameCollision,
            ProjectNameInvalid,
            ProjectPrivacyRestrictedException,
            ProjectsLimitReached,
        )

        error_processors: dict[str, Callable[[dict], Exception]] = {
            "ATTRIBUTES_PER_EXPERIMENT_LIMIT_EXCEEDED": lambda response_body: NeptuneFieldCountLimitExceedException(
                limit=response_body.get("limit", "<unknown limit>"),
                container_type=response_body.get("experimentType", "object"),
                identifier=response_body.get("experimentQualifiedName", "<unknown identifier>"),
            ),
            "AUTHORIZATION_TOKEN_EXPIRED": lambda _: NeptuneAuthTokenExpired(),
            "EXPERIMENT_NOT_FOUND": lambda _: ObjectNotFound(),
            "INCORRECT_IDENTIFIER": lambda response_body: IncorrectIdentifierException(
                identifier=response_body.get("identifier", "<Unknown identifier>")
            ),
            "LIMIT_OF_PROJECTS_REACHED": lambda _: ProjectsLimitReached(),
            "PROJECT_KEY_COLLISION": lambda response_body: ProjectKeyCollision(
                key=response_body.get("key", "<unknown key>")
            ),
            "PROJECT_KEY_INVALID": lambda response_body: ProjectKeyInvalid(
                key=response_body.get("key", "<unknown key>"),
                reason=response_body.get("reason", "Unknown reason"),
            ),
            "PROJECT_NAME_COLLISION": lambda response_body: ProjectNameCollision(
                key=response_body.get("key", "<unknown key>")
            ),
            "PROJECT_NAME_INVALID": lambda response_body: ProjectNameInvalid(
                name=response_body.get("name", "<unknown name>")
            ),
            "VISIBILITY_RESTRICTED": lambda response_body: ProjectPrivacyRestrictedException(
                requested=response_body.get("requestedValue"),
                allowed=response_body.get("allowedValues"),
            ),
            "WORKSPACE_IN_READ_ONLY_MODE": lambda response_body: NeptuneLimitExceedException(
                reason=response_body.get("title", "Unknown reason")
            ),
            "PROJECT_LIMITS_EXCEEDED": lambda response_body: NeptuneLimitExceedException(
                reason=response_body.get("title", "Unknown reason")
            ),
            "LIMIT_OF_ACTIVE_PROJECTS_REACHED": lambda response_body: ActiveProjectsLimitReachedException(
                currentQuota=response_body.get("currentQuota", "<unknown quota>")
            ),
            "WRITE_ACCESS_DENIED_TO_ARCHIVED_PROJECT": lambda _: WritingToArchivedProjectException(),
        }

        body = ensure_json_response(response)
        error_type: str | None = body.get("errorType")
        error_processor = error_processors.get(error_type)
        if error_processor:
            if exception:
                raise error_processor(body) from exception
            raise error_processor(body)

        if exception:
            raise exception

    def __call__(self, *args: object, **kwargs: object) -> FinishedApiResponseFuture:
        try:
            future = self._api_method(*args, **kwargs)
            return FinishedApiResponseFuture(future.response())  # wait synchronously
        except HTTPError as e:
            self.handle_neptune_http_errors(e.response, exception=e)

    def __getattr__(self, item: str) -> object:
        return getattr(self._api_method, item)


class ApiWrapper:
    def __init__(self, api_obj: object) -> None:
        self._api_obj = api_obj

    def __getattr__(self, item: str) -> ApiMethodWrapper:
        return ApiMethodWrapper(getattr(self._api_obj, item))


class FinishedApiResponseFuture:
    def __init__(self, response: object) -> None:
        self._response = response

    def response(self) -> object:
        return self._response


class SwaggerClientWrapper:
    def __init__(self, swagger_client: SwaggerClient):
        self._swagger_client = swagger_client
        self.api = ApiWrapper(swagger_client.api)
        self.swagger_spec = swagger_client.swagger_spec

    # For test purposes
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SwaggerClientWrapper):
            return self._swagger_client == other._swagger_client
        return False

    def __hash__(self) -> int:
        return hash(id(self._swagger_client))
