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
    "get_retry_from_headers_or_default",
    "register_queue_size_provider",
    "unregister_queue_size_provider",
    "with_api_exceptions_handler",
]

import itertools
import os
import random
import time
from typing import (
    Callable,
    ParamSpec,
    TypeVar,
)

from bravado.exception import (
    BravadoConnectionError,
    BravadoTimeoutError,
    HTTPBadGateway,
    HTTPClientError,
    HTTPForbidden,
    HTTPGatewayTimeout,
    HTTPInternalServerError,
    HTTPRequestTimeout,
    HTTPServiceUnavailable,
    HTTPTooManyRequests,
    HTTPUnauthorized,
)
from bravado_core.util import RecursiveCallException
import requests
from requests.exceptions import ChunkedEncodingError
from urllib3.exceptions import NewConnectionError

from minfx.neptune_v2.common.envs import NEPTUNE_RETRIES_TIMEOUT_ENV
from minfx.neptune_v2.common.exceptions import (
    ClientHttpError,
    Forbidden,
    NeptuneAuthTokenExpired,
    NeptuneConnectionLostException,
    NeptuneInvalidApiTokenException,
    NeptuneSSLVerificationError,
    Unauthorized,
)
from minfx.neptune_v2.common.utils import reset_internal_ssl_state
from minfx.neptune_v2.internal.utils.logger import get_logger

_logger = get_logger()

MAX_RETRY_TIME = 30
MAX_RETRY_MULTIPLIER = 10
retries_timeout = int(os.getenv(NEPTUNE_RETRIES_TIMEOUT_ENV, "120"))  # 2 minutes default

P = ParamSpec("P")
R = TypeVar("R")

# Global retry state tracker: backend_index -> current retry count (0 = not retrying)
# This allows external monitoring of inner retry loops
_retry_state: dict[int | None, int] = {}

# Global registry for queue size providers: backend_index -> callable returning queue size
# This allows retry logging to include the number of queued operations
_queue_size_providers: dict[int | None, Callable[[], int]] = {}


def get_retry_state(backend_index: int | None = None) -> int:
    """Get current retry count for a backend (0 = not retrying)."""
    return _retry_state.get(backend_index, 0)


def get_all_retry_states() -> dict[int | None, int]:
    """Get all current retry states."""
    return dict(_retry_state)


def register_queue_size_provider(backend_index: int | None, provider: Callable[[], int]) -> None:
    """Register a callable that returns the queue size for a backend.

    This allows retry logging to include the number of queued operations.
    """
    _queue_size_providers[backend_index] = provider


def unregister_queue_size_provider(backend_index: int | None) -> None:
    """Unregister the queue size provider for a backend."""
    _queue_size_providers.pop(backend_index, None)


def get_queue_size(backend_index: int | None = None) -> int | None:
    """Get the queue size for a backend, or None if no provider registered."""
    provider = _queue_size_providers.get(backend_index)
    if provider is not None:
        try:
            return provider()
        except Exception:
            return None
    return None


def get_retry_from_headers_or_default(headers: dict, retry_count: int) -> float:
    """Get retry delay from headers or compute exponential backoff.

    Args:
        headers: Response headers (may contain 'retry-after' in seconds)
        retry_count: Current retry attempt number for exponential backoff

    Returns:
        Wait time in seconds (supports fractional seconds)
    """
    try:
        return (
            float(headers["retry-after"][0])
            if "retry-after" in headers
            else float(2 ** min(MAX_RETRY_MULTIPLIER, retry_count))
        )
    except Exception:
        return float(min(2 ** min(MAX_RETRY_MULTIPLIER, retry_count), MAX_RETRY_TIME))


def _compute_wait_time(retry_num: int) -> float:
    """Compute wait time with exponential backoff and initial jitter.

    First retry: random 1-2 seconds (avoids thundering herd)
    Subsequent retries: 2^retry seconds, capped at MAX_RETRY_TIME
    """
    if retry_num == 0:
        # Random jitter between 1 and 2 seconds to avoid thundering herd
        return random.uniform(1.0, 2.0)
    return min(2 ** min(MAX_RETRY_MULTIPLIER, retry_num), MAX_RETRY_TIME)


def _log_retry(
    error: Exception,
    wait_time: float,
    retry_num: int,
    elapsed: float,
    timeout: float,
    backend_index: int | None = None,
) -> None:
    """Log a retry attempt with timing information."""
    error_name = type(error).__name__
    remaining = max(0, timeout - elapsed)
    backend_prefix = f"[backend {backend_index}] " if backend_index is not None else ""

    # Try to get queue size for additional context
    queue_size = get_queue_size(backend_index)
    queue_suffix = f", {queue_size} queued ops" if queue_size is not None else ""

    _logger.warning(
        "%sConnection error: %s. Retrying in %.1fs... (attempt %d, %.0fs remaining%s)",
        backend_prefix,
        error_name,
        wait_time,
        retry_num + 1,
        remaining,
        queue_suffix,
    )


def _log_retry_success(
    retry_num: int,
    elapsed: float,
    backend_index: int | None = None,
) -> None:
    """Log when a retry finally succeeds."""
    backend_prefix = f"[backend {backend_index}] " if backend_index is not None else ""

    # Try to get queue size for additional context
    queue_size = get_queue_size(backend_index)
    queue_suffix = f", {queue_size} queued ops" if queue_size is not None else ""

    _logger.info(
        "%sConnection restored after %d retries (%.1fs elapsed%s)",
        backend_prefix,
        retry_num,
        elapsed,
        queue_suffix,
    )


def with_api_exceptions_handler(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ssl_error_occurred = False
        last_exception = None
        start_time = time.monotonic()

        # Extract backend_index from kwargs first (for module-level functions),
        # or from self if this is a method call on a backend object
        backend_index: int | None = kwargs.get("backend_index")
        if backend_index is None and args and hasattr(args[0], "backend_index"):
            backend_index = args[0].backend_index

        retried_errors = 0  # Track number of logged retries for success message

        def _update_retry_state(count: int) -> None:
            """Update global retry state for monitoring."""
            if count > 0:
                _retry_state[backend_index] = count
            elif backend_index in _retry_state:
                del _retry_state[backend_index]

        try:
            for retry in itertools.count(0):
                elapsed = time.monotonic() - start_time
                if elapsed > retries_timeout:
                    break

                try:
                    result = func(*args, **kwargs)
                    # Log success if we had retried errors
                    if retried_errors > 0:
                        _log_retry_success(retried_errors, elapsed, backend_index)
                    return result
                except requests.exceptions.InvalidHeader as e:
                    if "X-Neptune-Api-Token" in e.args[0]:
                        raise NeptuneInvalidApiTokenException
                    raise
                except requests.exceptions.SSLError as e:
                    """
                    OpenSSL's internal random number generator does not properly handle forked processes.
                    Applications must change the PRNG state of the parent process
                    if they use any SSL feature with os.fork().
                    Any successful call of RAND_add(), RAND_bytes() or RAND_pseudo_bytes() is sufficient.
                    https://docs.python.org/3/library/ssl.html#multi-processing
                    On Linux it looks like it does not help much but does not break anything either.
                    But single retry seems to solve the issue.
                    """
                    if not ssl_error_occurred:
                        ssl_error_occurred = True
                        reset_internal_ssl_state()
                        continue

                    if "CertificateError" in str(e.__context__):
                        raise NeptuneSSLVerificationError from e
                    wait_time = _compute_wait_time(retry)
                    _log_retry(e, wait_time, retry, elapsed, retries_timeout, backend_index)
                    retried_errors += 1
                    _update_retry_state(retried_errors)
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                except (
                    BravadoConnectionError,
                    BravadoTimeoutError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    HTTPRequestTimeout,
                    HTTPServiceUnavailable,
                    HTTPGatewayTimeout,
                    HTTPBadGateway,
                    HTTPInternalServerError,
                    NewConnectionError,
                    ChunkedEncodingError,
                    RecursiveCallException,
                ) as e:
                    wait_time = _compute_wait_time(retry)
                    _log_retry(e, wait_time, retry, elapsed, retries_timeout, backend_index)
                    retried_errors += 1
                    _update_retry_state(retried_errors)
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                except HTTPTooManyRequests as e:
                    wait_time = get_retry_from_headers_or_default(e.response.headers, retry)
                    _log_retry(e, wait_time, retry, elapsed, retries_timeout, backend_index)
                    retried_errors += 1
                    _update_retry_state(retried_errors)
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                except NeptuneAuthTokenExpired as e:
                    last_exception = e
                    continue
                except HTTPUnauthorized:
                    raise Unauthorized
                except HTTPForbidden:
                    raise Forbidden
                except HTTPClientError as e:
                    raise ClientHttpError(e.status_code, e.response.text) from e
                except requests.exceptions.RequestException as e:
                    if e.response is None:
                        raise
                    status_code = e.response.status_code
                    if status_code in (
                        HTTPRequestTimeout.status_code,
                        HTTPBadGateway.status_code,
                        HTTPServiceUnavailable.status_code,
                        HTTPGatewayTimeout.status_code,
                        HTTPInternalServerError.status_code,
                    ):
                        wait_time = _compute_wait_time(retry)
                        _log_retry(e, wait_time, retry, elapsed, retries_timeout, backend_index)
                        retried_errors += 1
                        _update_retry_state(retried_errors)
                        time.sleep(wait_time)
                        last_exception = e
                        continue
                    if status_code == HTTPTooManyRequests.status_code:
                        wait_time = get_retry_from_headers_or_default(e.response.headers, retry)
                        _log_retry(e, wait_time, retry, elapsed, retries_timeout, backend_index)
                        retried_errors += 1
                        _update_retry_state(retried_errors)
                        time.sleep(wait_time)
                        last_exception = e
                        continue
                    if status_code == HTTPUnauthorized.status_code:
                        raise Unauthorized
                    if status_code == HTTPForbidden.status_code:
                        raise Forbidden
                    if 400 <= status_code < 500:
                        raise ClientHttpError(status_code, e.response.text) from e
                    raise
            raise NeptuneConnectionLostException(last_exception) from last_exception
        finally:
            # Clear retry state when done (success or failure)
            _update_retry_state(0)

    return wrapper
