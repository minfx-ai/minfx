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

__all__ = ["NEPTUNE_LOGGER_NAME", "get_disabled_logger", "get_logger"]

import logging
import os
import re
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO

# Pattern to match [backend N] at the start of messages
BACKEND_PATTERN = re.compile(r"^\[backend (\d+)\] ")

NEPTUNE_LOGGER_NAME = "minfx"
NEPTUNE_NO_PREFIX_LOGGER_NAME = "minfx_no_prefix"
NEPTUNE_NOOP_LOGGER_NAME = "minfx_noop"
LOG_FORMAT = "%(asctime)s.%(msecs)03.0f [%(levelname)s] [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
NO_PREFIX_FORMAT = "%(message)s"


class AnsiColors:
    """ANSI escape codes for terminal colors."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


def _should_use_colors() -> bool:
    """Determine if terminal colors should be used.

    Returns True if:
    - MINFX_LOG_COLOR=1 (force on)
    - MINFX_LOG_COLOR is unset and stderr is a TTY

    Returns False if:
    - MINFX_LOG_COLOR=0 (force off)
    - NO_COLOR env var is set (standard for disabling colors)
    - stderr is not a TTY (e.g., piped output)
    """
    # Check for explicit color preference
    color_env = os.environ.get("MINFX_LOG_COLOR", "").lower()
    if color_env in ("1", "true", "yes", "on"):
        return True
    if color_env in ("0", "false", "no", "off"):
        return False

    # Respect NO_COLOR standard (https://no-color.org/)
    if os.environ.get("NO_COLOR") is not None:
        return False

    # Auto-detect based on TTY
    try:
        return sys.stderr.isatty()
    except Exception:
        return False


class CustomFormatter(logging.Formatter):
    """Custom formatter with UTC timestamps, lowercase level names, and optional colors."""

    converter = time.gmtime  # Use UTC time

    # Color mapping for log levels
    LEVEL_COLORS = {
        logging.DEBUG: AnsiColors.BRIGHT_BLUE,
        logging.INFO: AnsiColors.BRIGHT_GREEN,
        logging.WARNING: AnsiColors.BRIGHT_YELLOW,
        logging.ERROR: AnsiColors.BRIGHT_RED,
        logging.CRITICAL: AnsiColors.BOLD + AnsiColors.BRIGHT_RED,
    }

    def __init__(self, use_colors: bool | None = None) -> None:
        super().__init__()
        # None means "auto-detect on each call" to handle env var changes
        self._use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        record.levelname = record.levelname.lower()

        # Check colors dynamically if not explicitly set (allows env var changes)
        use_colors = self._use_colors if self._use_colors is not None else _should_use_colors()

        if use_colors:
            return self._format_colored(record)
        return self._format_plain(record)

    def _format_plain(self, record: logging.LogRecord) -> str:
        """Format log record without colors."""
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        formatter.converter = time.gmtime
        return formatter.format(record)

    def _format_colored(self, record: logging.LogRecord) -> str:
        """Format log record with terminal colors."""
        # Get level color
        level_color = self.LEVEL_COLORS.get(record.levelno, AnsiColors.RESET)

        # Format timestamp with dim cyan
        timestamp = time.strftime(LOG_DATE_FORMAT, time.gmtime(record.created))
        msecs = f"{record.msecs:03.0f}"
        colored_timestamp = f"{AnsiColors.DIM}{AnsiColors.CYAN}{timestamp}.{msecs}{AnsiColors.RESET}"

        # Format level with appropriate color
        colored_level = f"{level_color}[{record.levelname}]{AnsiColors.RESET}"

        # Format logger name with dim magenta
        colored_name = f"{AnsiColors.DIM}{AnsiColors.MAGENTA}[{record.name}]{AnsiColors.RESET}"

        # Format message with colored backend identifier if present
        message = self._colorize_backend_id(record.getMessage())

        return f"{colored_timestamp} {colored_level} {colored_name} {message}"

    def _colorize_backend_id(self, message: str) -> str:
        """Colorize [backend N] prefix in message if present."""
        match = BACKEND_PATTERN.match(message)
        if match:
            backend_num = match.group(1)
            colored_backend = f"{AnsiColors.BRIGHT_CYAN}[backend {backend_num}]{AnsiColors.RESET}"
            return colored_backend + " " + message[match.end() :]
        return message


class GrabbableStderrHandler(logging.StreamHandler):
    """StreamHandler that always uses current sys.stderr with auto-flush.

    This ensures logs are written to stderr and flushed immediately,
    which means they appear even when piped through tools like tee.
    Falls back to /dev/tty if the pipe is broken (e.g., tee died on SIGINT).
    Based on logging._StderrHandler from standard library.
    """

    def __init__(self, level: int = logging.NOTSET) -> None:
        logging.Handler.__init__(self, level)

    @property
    def stream(self) -> TextIO:
        return sys.stderr

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record with immediate flush and fallback on pipe failure."""
        try:
            super().emit(record)
            self.flush()
        except BrokenPipeError:
            # Pipe broke (e.g., tee died on SIGINT), try writing to terminal directly
            self._emit_to_tty(record)

    def _emit_to_tty(self, record: logging.LogRecord) -> None:
        """Try to write directly to the controlling terminal as a fallback."""
        try:
            with open("/dev/tty", "w") as tty:
                msg = self.format(record)
                tty.write(msg + self.terminator)
                tty.flush()
        except Exception:
            pass  # Best effort - nothing more we can do


def get_logger(with_prefix: bool = True) -> logging.Logger:
    name = NEPTUNE_LOGGER_NAME if with_prefix else NEPTUNE_NO_PREFIX_LOGGER_NAME

    return logging.getLogger(name)


def get_disabled_logger() -> logging.Logger:
    return logging.getLogger(NEPTUNE_NOOP_LOGGER_NAME)


def _set_up_logging():
    # setup neptune logger so that logging.getLogger(NEPTUNE_LOGGER_NAME)
    # returns configured logger
    neptune_logger = logging.getLogger(NEPTUNE_LOGGER_NAME)
    neptune_logger.propagate = False

    stderr_handler = GrabbableStderrHandler()
    stderr_handler.setFormatter(CustomFormatter())
    neptune_logger.addHandler(stderr_handler)

    neptune_logger.setLevel(logging.INFO)


def _set_up_no_prefix_logging():
    neptune_logger = logging.getLogger(NEPTUNE_NO_PREFIX_LOGGER_NAME)
    neptune_logger.propagate = False

    stderr_handler = GrabbableStderrHandler()
    stderr_handler.setFormatter(logging.Formatter(NO_PREFIX_FORMAT))
    neptune_logger.addHandler(stderr_handler)

    neptune_logger.setLevel(logging.INFO)


def _set_up_disabled_logging():
    neptune_logger = logging.getLogger(NEPTUNE_NOOP_LOGGER_NAME)

    neptune_logger.setLevel(logging.CRITICAL)


_set_up_logging()
_set_up_no_prefix_logging()
_set_up_disabled_logging()
