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

__all__ = ["instance"]

from platform import node as get_hostname
import sys
import threading
import traceback
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Type,
)

from minfx.neptune_v2.internal.utils.logger import get_logger

if TYPE_CHECKING:
    import uuid

_logger = get_logger()

SYS_UNCAUGHT_EXCEPTION_HANDLER_TYPE = Callable[[Type[BaseException], BaseException, Optional[TracebackType]], Any]


class UncaughtExceptionHandler:
    def __init__(self) -> None:
        self._previous_uncaught_exception_handler: SYS_UNCAUGHT_EXCEPTION_HANDLER_TYPE | None = None
        self._handlers: dict[uuid.UUID, Callable[[list[str]], None]] = {}
        self._lock = threading.Lock()
        self._last_exception_type: type[BaseException] | None = None

    def trigger(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        header_lines = [
            f"An uncaught exception occurred while run was active on worker {get_hostname()}.",
            "Marking run as failed",
            "Traceback:",
        ]

        traceback_lines = header_lines + traceback.format_tb(exc_tb) + str(exc_val).split("\n")
        for handler in self._handlers.values():
            handler(traceback_lines)

    def activate(self) -> None:
        with self._lock:
            if self._previous_uncaught_exception_handler is not None:
                return
            self._previous_uncaught_exception_handler = sys.excepthook
            sys.excepthook = self.exception_handler

    def deactivate(self) -> None:
        with self._lock:
            if self._previous_uncaught_exception_handler is None:
                return
            sys.excepthook = self._previous_uncaught_exception_handler
            self._previous_uncaught_exception_handler = None

    def register(self, uid: uuid.UUID, handler: Callable[[list[str]], None]) -> None:
        with self._lock:
            self._handlers[uid] = handler

    def unregister(self, uid: uuid.UUID) -> None:
        with self._lock:
            if uid in self._handlers:
                del self._handlers[uid]

    def exception_handler(self, *args: Any, **kwargs: Any) -> None:
        # Store the exception type for shutdown reason detection
        if args:
            self._last_exception_type = args[0]

        self.trigger(*args, **kwargs)

        if self._previous_uncaught_exception_handler is not None:
            self._previous_uncaught_exception_handler(*args, **kwargs)

    def get_shutdown_reason(self) -> str:
        """Get the reason for shutdown based on captured exception info."""
        if self._last_exception_type is None:
            return "completed"
        if self._last_exception_type is KeyboardInterrupt:
            return "interrupted"
        return f"exception ({self._last_exception_type.__name__})"


instance = UncaughtExceptionHandler()
