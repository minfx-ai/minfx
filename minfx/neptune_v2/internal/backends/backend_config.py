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
"""BackendConfig and token parsing utilities for multi-backend support."""

from __future__ import annotations

__all__ = [
    "BackendConfig",
    "all_backends_have_projects",
    "configs_from_tokens",
    "get_first_backend_project",
    "parse_api_tokens",
    "validate_backends_unique",
]

import os
from dataclasses import dataclass

from minfx.neptune_v2.common.envs import API_TOKEN_ENV_NAME
from minfx.neptune_v2.exceptions import (
    NeptuneDuplicateBackendError,
    NeptuneMissingApiTokenException,
)


@dataclass
class BackendConfig:
    """Configuration for a single backend connection.

    Attributes:
        api_token: The API token for authenticating with the backend.
        proxies: Optional proxy configuration for HTTP requests.
        project: Optional project name override (e.g. "workspace/project").
            If None, uses the main project from Run(project=...) or NEPTUNE_PROJECT env.
    """

    api_token: str
    proxies: dict[str, str] | None = None
    project: str | None = None


def parse_api_tokens(api_token: str | None) -> list[str]:
    """Parse comma-separated API tokens into a list.

    If api_token is None, reads from the NEPTUNE_API_TOKEN environment variable.

    Note: API tokens are base64-encoded JSON, which uses only A-Za-z0-9+/= characters.
    Commas are NOT valid base64 characters, so comma separation is safe.

    Args:
        api_token: Comma-separated API tokens or None to read from env.

    Returns:
        List of individual API tokens.

    Raises:
        NeptuneMissingApiTokenException: If no token is provided or found in env.
    """
    if api_token is None:
        api_token = os.getenv(API_TOKEN_ENV_NAME)

    if api_token is None:
        raise NeptuneMissingApiTokenException()

    tokens = [t.strip() for t in api_token.split(",")]
    return [t for t in tokens if t]  # Filter empty strings


def configs_from_tokens(
    api_tokens: str | list[str] | None,
    proxies: dict[str, str] | None = None,
    project: str | None = None,
) -> list[BackendConfig]:
    """Create BackendConfig list from tokens.

    Args:
        api_tokens: Either a comma-separated string, a list of tokens, or None.
        proxies: Optional proxy configuration to apply to all backends.
        project: Optional default project for all backends (can be overridden per-backend).

    Returns:
        List of BackendConfig objects, one per token.
    """
    if isinstance(api_tokens, str):
        tokens = parse_api_tokens(api_tokens)
    elif api_tokens is None:
        tokens = parse_api_tokens(None)
    else:
        tokens = api_tokens

    return [BackendConfig(api_token=token, proxies=proxies, project=project) for token in tokens]


def validate_backends_unique(backends: list[BackendConfig]) -> None:
    """Validate that all backends have unique API tokens.

    Backends are considered duplicates if they have the same api_token.

    Note: Two different tokens could theoretically point to the same server,
    but we only validate token equality (not URL extraction) because:
    - Same token = definitely same backend (reject)
    - Different tokens = user's explicit intent to use both (allow)

    Args:
        backends: List of BackendConfig objects.

    Raises:
        NeptuneDuplicateBackendError: If duplicate backends are detected.
    """
    seen_tokens: set[str] = set()
    for i, config in enumerate(backends):
        if config.api_token in seen_tokens:
            raise NeptuneDuplicateBackendError(f"Duplicate backend at index {i}: same api_token used multiple times")
        seen_tokens.add(config.api_token)


def all_backends_have_projects(backends: list[BackendConfig] | None) -> bool:
    """Check if all backends have their own project specified.

    Args:
        backends: List of BackendConfig objects.

    Returns:
        True if backends is not None/empty and ALL backends have a project specified.
    """
    if not backends:
        return False
    return all(config.project is not None for config in backends)


def get_first_backend_project(backends: list[BackendConfig] | None) -> str | None:
    """Get the project from the first backend config.

    Args:
        backends: List of BackendConfig objects.

    Returns:
        The project from the first backend, or None if no backends or no project.
    """
    if not backends:
        return None
    return backends[0].project
