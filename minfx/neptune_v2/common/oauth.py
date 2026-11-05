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

import contextlib
import os
import threading
import time
from typing import (
    TYPE_CHECKING,
    Callable,
)

from bravado.exception import (
    HTTPUnauthorized,
)
from bravado.requests_client import Authenticator
from requests.auth import AuthBase
from requests import Request

from minfx.neptune_v2.common.backends.utils import with_api_exceptions_handler
from minfx.neptune_v2.envs import PROJECT_ENV_NAME

if TYPE_CHECKING:
    from requests import PreparedRequest
from minfx.neptune_v2.common.exceptions import (
    NeptuneInvalidApiTokenException,
)
from minfx.neptune_v2.common.utils import update_session_proxies
from minfx.neptune_v2.exceptions import NeptuneMissingProjectNameException
from minfx.neptune_v2.internal.backends.utils import (
    build_operation_url,
    handle_server_raw_response_messages,
)

AUTH_TOKEN_TTL_SECS = 5 * 60
BACKEND_AUTH_PATH = "/api/v1/auth/backend"


class NeptuneAuth(AuthBase):
    __LOCK = threading.RLock()

    def __init__(self, access_token_factory: Callable[[str | None], str], default_project_name: str | None) -> None:
        self._access_token_factory = access_token_factory
        self._project_name = default_project_name
        self._access_token: str | None = None
        self._token_created_at = 0.0

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        self.refresh_token_if_needed()
        return self._add_token(r)

    def _add_token(self, r: PreparedRequest) -> PreparedRequest:
        if self._access_token is None:
            self._refresh_token()
        r.headers["Authorization"] = f"Bearer {self._access_token}"
        return r

    @with_api_exceptions_handler
    def refresh_token_if_needed(self, project_name_hint: str | None = None) -> None:
        if project_name_hint is not None:
            self._project_name = project_name_hint
        if self._access_token is None:
            self._refresh_token()
            return
        if time.time() - self._token_created_at >= AUTH_TOKEN_TTL_SECS:
            self._refresh_token()

    def _refresh_token(self) -> None:
        with self.__LOCK:
            self._access_token = self._access_token_factory(self._project_name)
            self._token_created_at = time.time()


class NeptuneAuthenticator(Authenticator):
    def __init__(
        self,
        api_token: str,
        backend_client: object,
        ssl_verify: bool,
        proxies: dict | None,
        project_name: str | None,
    ) -> None:
        super().__init__(host="")

        # We need to pass a lambda to re-create fresh session token when needed.
        def access_token_factory(project_name_hint: str | None) -> str:
            organization_name, workspace_name = _resolve_project_name_parts(project_name_hint)
            request_body = {
                "api_token": api_token,
                "project_name": f"{organization_name}/{workspace_name}",
            }
            request_url = build_operation_url(backend_client.swagger_spec.api_url, BACKEND_AUTH_PATH)
            request = Request(method="POST", url=request_url, json=request_body)

            prepared_request = backend_client.swagger_spec.http_client.session.prepare_request(request)
            with contextlib.suppress(Exception):
                update_session_proxies(backend_client.swagger_spec.http_client.session, proxies)

            try:
                response = handle_server_raw_response_messages(
                    backend_client.swagger_spec.http_client.session.send(
                        prepared_request,
                        verify=ssl_verify,
                    )
                )
            except HTTPUnauthorized:
                raise NeptuneInvalidApiTokenException

            if response.status_code == HTTPUnauthorized.status_code:
                raise NeptuneInvalidApiTokenException
            response.raise_for_status()

            response_data = response.json()
            session_tokens = response_data.get("session_tokens", {})
            access_token = session_tokens.get("access_token")
            if not isinstance(access_token, str) or access_token == "":
                raise NeptuneInvalidApiTokenException
            return access_token

        self.auth = NeptuneAuth(access_token_factory, project_name)

    def matches(self, url: str) -> bool:
        return True

    def apply(self, request: PreparedRequest) -> PreparedRequest:
        self.auth.refresh_token_if_needed(_extract_project_name_hint(request))
        request.auth = self.auth
        return request


def _resolve_project_name_parts(project_name: str | None) -> tuple[str, str]:
    normalized_project_name = project_name
    if normalized_project_name is None:
        normalized_project_name = os.getenv(PROJECT_ENV_NAME)
    if normalized_project_name is None:
        raise NeptuneMissingProjectNameException()

    project_parts = normalized_project_name.split("/", maxsplit=1)
    if len(project_parts) != 2:
        raise NeptuneMissingProjectNameException()
    organization_name, workspace_name = project_parts
    if organization_name == "" or workspace_name == "":
        raise NeptuneMissingProjectNameException()
    return organization_name, workspace_name


def _extract_project_name_hint(request: PreparedRequest) -> str | None:
    request_params = getattr(request, "params", None)
    if isinstance(request_params, dict):
        project_identifier = request_params.get("projectIdentifier")
        if isinstance(project_identifier, str):
            return project_identifier
    return None
