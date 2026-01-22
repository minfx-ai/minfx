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
    "DEFAULT_REQUEST_KWARGS",
    "create_artifacts_client",
    "create_backend_client",
    "create_http_client_with_auth",
    "create_leaderboard_client",
]

import contextlib
import os
import platform
from typing import (
    TYPE_CHECKING,
)

from bravado.requests_client import RequestsClient

from minfx.neptune_v2.common.backends.utils import with_api_exceptions_handler
from minfx.neptune_v2.common.oauth import NeptuneAuthenticator
from minfx.neptune_v2.envs import NEPTUNE_REQUEST_TIMEOUT
from minfx.neptune_v2.exceptions import NeptuneClientUpgradeRequiredError
from minfx.neptune_v2.internal.backends.api_model import ClientConfig
from minfx.neptune_v2.internal.backends.swagger_client_wrapper import SwaggerClientWrapper
from minfx.neptune_v2.internal.backends.utils import (
    NeptuneResponseAdapter,
    build_operation_url,
    cache,
    create_swagger_client,
    update_session_proxies,
    verify_client_version,
    verify_host_resolution,
)
from minfx.neptune_v2.version import version as neptune_client_version

if TYPE_CHECKING:
    from bravado.http_client import HttpClient
    import requests

    from minfx.neptune_v2.internal.credentials import Credentials

BACKEND_SWAGGER_PATH = "/api/backend/swagger.json"
LEADERBOARD_SWAGGER_PATH = "/api/leaderboard/swagger.json"
ARTIFACTS_SWAGGER_PATH = "/api/artifacts/swagger.json"

CONNECT_TIMEOUT = 30  # helps detecting internet connection lost
REQUEST_TIMEOUT = int(os.getenv(NEPTUNE_REQUEST_TIMEOUT, "600"))

DEFAULT_REQUEST_KWARGS = {
    "_request_options": {
        "connect_timeout": CONNECT_TIMEOUT,
        "timeout": REQUEST_TIMEOUT,
        "headers": {"X-Neptune-LegacyClient": "false"},
    }
}


def _close_connections_on_fork(session: requests.Session):
    with contextlib.suppress(AttributeError):
        os.register_at_fork(before=session.close, after_in_child=session.close, after_in_parent=session.close)


# WARNING: Be careful when changing this function. It is used in the experimental package
def _set_pool_size(http_client: RequestsClient) -> None:
    _ = http_client


def create_http_client(ssl_verify: bool, proxies: dict[str, str]) -> RequestsClient:
    http_client = RequestsClient(ssl_verify=ssl_verify, response_adapter_class=NeptuneResponseAdapter)
    http_client.session.verify = ssl_verify

    _set_pool_size(http_client)

    _close_connections_on_fork(http_client.session)

    update_session_proxies(http_client.session, proxies)

    user_agent = f"neptune-client/{neptune_client_version} ({platform.platform()}, python {platform.python_version()})"
    http_client.session.headers.update({"User-Agent": user_agent})

    return http_client


@cache
def _get_token_client(
    credentials: Credentials,
    ssl_verify: bool,
    proxies: dict[str, str],
    backend_index: int | None = None,
) -> SwaggerClientWrapper:
    api_url = credentials.api_url_opt or credentials.token_origin_address
    if proxies is None:
        verify_host_resolution(api_url)

    token_http_client = create_http_client(ssl_verify, proxies)

    return SwaggerClientWrapper(
        create_swagger_client(
            build_operation_url(api_url, BACKEND_SWAGGER_PATH),
            token_http_client,
            backend_index=backend_index,
        )
    )


@cache
@with_api_exceptions_handler
def get_client_config(
    credentials: Credentials,
    ssl_verify: bool,
    proxies: dict[str, str],
    backend_index: int | None = None,
) -> ClientConfig:
    backend_client = _get_token_client(
        credentials=credentials,
        ssl_verify=ssl_verify,
        proxies=proxies,
        backend_index=backend_index,
    )

    config = (
        backend_client.api.getClientConfig(
            X_Neptune_Api_Token=credentials.api_token,
            alpha="true",
            **DEFAULT_REQUEST_KWARGS,
        )
        .response()
        .result
    )

    client_config = ClientConfig.from_api_response(config)
    if not client_config.version_info:
        raise NeptuneClientUpgradeRequiredError(neptune_client_version, max_version="0.4.111")
    return client_config


@cache
def create_http_client_with_auth(
    credentials: Credentials,
    ssl_verify: bool,
    proxies: dict[str, str],
    backend_index: int | None = None,
) -> tuple[RequestsClient, ClientConfig, str]:
    """Create authenticated HTTP client.

    Returns:
        Tuple of (http_client, client_config, api_url) where api_url is the
        canonical URL from the token to use for all API calls.
    """
    client_config = get_client_config(
        credentials=credentials,
        ssl_verify=ssl_verify,
        proxies=proxies,
        backend_index=backend_index,
    )

    # Use token's api_url as the single source of truth for API URL
    api_url = credentials.api_url_opt or credentials.token_origin_address

    verify_client_version(client_config, neptune_client_version)

    http_client = create_http_client(ssl_verify=ssl_verify, proxies=proxies)
    http_client.authenticator = NeptuneAuthenticator(
        credentials.api_token,
        _get_token_client(
            credentials=credentials,
            ssl_verify=ssl_verify,
            proxies=proxies,
            backend_index=backend_index,
        ),
        ssl_verify,
        proxies,
    )

    return http_client, client_config, api_url


@cache
def create_backend_client(api_url: str, http_client: HttpClient) -> SwaggerClientWrapper:
    return SwaggerClientWrapper(
        create_swagger_client(
            build_operation_url(api_url, BACKEND_SWAGGER_PATH),
            http_client,
        )
    )


@cache
def create_leaderboard_client(api_url: str, http_client: HttpClient) -> SwaggerClientWrapper:
    return SwaggerClientWrapper(
        create_swagger_client(
            build_operation_url(api_url, LEADERBOARD_SWAGGER_PATH),
            http_client,
        )
    )


@cache
def create_artifacts_client(api_url: str, http_client: HttpClient) -> SwaggerClientWrapper:
    return SwaggerClientWrapper(
        create_swagger_client(
            build_operation_url(api_url, ARTIFACTS_SWAGGER_PATH),
            http_client,
        )
    )
