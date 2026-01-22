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
"""Backend name utilities for multi-backend support.

This module provides functions to derive filesystem-safe backend names from URLs,
enabling the CLI to match directories to their backend servers via NEPTUNE_API_TOKEN.
"""

from __future__ import annotations

__all__ = [
    "backend_name_from_url",
    "backend_address_from_url",
    "url_matches_backend_name",
    "get_backend_name_from_token",
    "is_named_backend_directory",
]

import base64
import json
from urllib.parse import urlparse


def backend_name_from_url(url: str) -> str:
    """Derive filesystem-safe backend name from URL.

    Uses DNS + port only (no scheme). Port defaults based on scheme if not specified.

    Examples:
        http://neptune2.localhost:8889  -> neptune2_localhost_8889
        https://app.neptune.ai          -> app_neptune_ai_443
        http://localhost                -> localhost_80

    Args:
        url: The backend URL (e.g., http://neptune2.localhost:8889)

    Returns:
        A filesystem-safe backend name derived from DNS and port.
    """
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    # Replace dots with underscores for filesystem safety
    safe_host = host.replace(".", "_")
    return f"{safe_host}_{port}"


def backend_address_from_url(url: str) -> str:
    """Extract DNS:port identifier from URL (for metadata storage).

    Examples:
        http://neptune2.localhost:8889  -> neptune2.localhost:8889
        https://app.neptune.ai          -> app.neptune.ai:443

    Args:
        url: The backend URL.

    Returns:
        The backend address in DNS:port format.
    """
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return f"{host}:{port}"


def url_matches_backend_name(url: str, backend_name: str) -> bool:
    """Check if a URL corresponds to a backend directory name.

    Args:
        url: The backend URL.
        backend_name: The backend directory name.

    Returns:
        True if the URL matches the backend name.
    """
    return backend_name_from_url(url) == backend_name


def get_backend_name_from_token(api_token: str) -> str | None:
    """Extract backend name from API token.

    API token is base64-encoded JSON containing api_address (and optionally api_url).
    We use api_address as the canonical backend identifier.

    Args:
        api_token: The base64-encoded API token.

    Returns:
        The backend name derived from the token, or None if invalid.
    """
    try:
        decoded = json.loads(base64.b64decode(api_token.strip().encode()).decode("utf-8"))
        # api_address is the canonical backend URL in tokens
        api_url = decoded.get("api_address")
        if api_url:
            return backend_name_from_url(api_url)
        return None
    except Exception:
        return None


def is_named_backend_directory(name: str) -> bool:
    """Check if a directory name is a named backend directory (DNS_port format).

    Named backend directories have format: {dns}_{port} where the last segment
    after the final underscore is numeric (the port).

    This explicitly excludes the legacy "backend_N" format where N is a small index.

    Examples:
        neptune2_localhost_8889 -> True (host=neptune2.localhost, port=8889)
        app_neptune_ai_443      -> True (host=app.neptune.ai, port=443)
        localhost_80            -> True (host=localhost, port=80)
        backend_0               -> False (old numeric index format)
        backend_1               -> False (old numeric index format)
        some_dir                -> False (not a valid port)

    Args:
        name: The directory name to check.

    Returns:
        True if the name matches the named backend format.
    """
    if "_" not in name:
        return False

    # Explicitly exclude legacy "backend_N" format
    if name.startswith("backend_"):
        suffix = name[len("backend_") :]
        # Legacy format has just a simple integer index (0, 1, 2, etc.)
        if suffix.isdigit():
            return False

    parts = name.rsplit("_", 1)
    if len(parts) != 2:
        return False
    last_part = parts[1]
    # Must be a valid port number (numeric, 1-65535)
    if not last_part.isdigit():
        return False
    port = int(last_part)
    return 1 <= port <= 65535


# ============================================================================
# Tests
# ============================================================================
def _run_tests() -> None:
    """Run unit tests for backend name utilities."""
    # Test backend_name_from_url
    assert backend_name_from_url("http://neptune2.localhost:8889") == "neptune2_localhost_8889"
    assert backend_name_from_url("https://app.neptune.ai") == "app_neptune_ai_443"
    assert backend_name_from_url("http://localhost") == "localhost_80"
    assert backend_name_from_url("https://localhost:9000") == "localhost_9000"
    assert backend_name_from_url("http://my.deep.nested.domain:1234") == "my_deep_nested_domain_1234"

    # Test backend_address_from_url
    assert backend_address_from_url("http://neptune2.localhost:8889") == "neptune2.localhost:8889"
    assert backend_address_from_url("https://app.neptune.ai") == "app.neptune.ai:443"
    assert backend_address_from_url("http://localhost") == "localhost:80"

    # Test url_matches_backend_name
    assert url_matches_backend_name("http://neptune2.localhost:8889", "neptune2_localhost_8889") is True
    assert url_matches_backend_name("http://neptune2.localhost:8889", "neptune2_localhost_8890") is False
    assert url_matches_backend_name("https://app.neptune.ai", "app_neptune_ai_443") is True

    # Test get_backend_name_from_token
    # Create a test token
    test_token_data = {"api_address": "http://neptune2.localhost:8889"}
    test_token = base64.b64encode(json.dumps(test_token_data).encode()).decode()
    assert get_backend_name_from_token(test_token) == "neptune2_localhost_8889"

    # Test with whitespace
    assert get_backend_name_from_token(f"  {test_token}  ") == "neptune2_localhost_8889"

    # Test invalid token
    assert get_backend_name_from_token("invalid_token") is None
    assert get_backend_name_from_token("") is None

    # Test token without api_address
    empty_token = base64.b64encode(json.dumps({}).encode()).decode()
    assert get_backend_name_from_token(empty_token) is None

    # Test is_named_backend_directory
    assert is_named_backend_directory("neptune2_localhost_8889") is True
    assert is_named_backend_directory("app_neptune_ai_443") is True
    assert is_named_backend_directory("localhost_80") is True
    assert is_named_backend_directory("localhost_8889") is True
    assert is_named_backend_directory("backend_0") is False  # legacy index format
    assert is_named_backend_directory("backend_1") is False  # legacy index format
    assert is_named_backend_directory("backend_10") is False  # legacy index format
    assert is_named_backend_directory("some_dir") is False  # not a number
    assert is_named_backend_directory("nounderscores") is False
    assert is_named_backend_directory("port_99999") is False  # port > 65535

    print("All backend_name tests passed!")


if __name__ == "__main__":
    _run_tests()
