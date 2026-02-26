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

__all__ = ["StderrCaptureLogger", "StdoutCaptureLogger"]

from queue import Queue
import sys
import threading
from typing import TYPE_CHECKING, TextIO

from minfx.neptune_v2.internal.threading.daemon import Daemon
from minfx.neptune_v2.logging import Logger as NeptuneLogger

if TYPE_CHECKING:
    from minfx.neptune_v2.metadata_containers import MetadataContainer


class StdStreamCaptureLogger:
    """Captures stdout/stderr and logs complete lines to Neptune.

    Uses line buffering to ensure each log entry contains a complete line,
    rather than fragmenting output (e.g., "hello" and "\\n" as separate entries).
    """

    def __init__(self, container: MetadataContainer, attribute_name: str, stream: TextIO):
        self._logger = NeptuneLogger(container, attribute_name)
        self.stream = stream
        self._thread_local = threading.local()
        self.enabled = True
        self._log_data_queue: Queue[str | None] = Queue()
        self._line_buffer = ""
        self._buffer_lock = threading.Lock()
        self._logging_thread = self.ReportingThread(self, "NeptuneThread_" + attribute_name)
        self._logging_thread.start()

    def pause(self):
        self._log_data_queue.put_nowait(None)
        self._logging_thread.pause()

    def resume(self):
        self._logging_thread.resume()

    def write(self, data: str) -> None:
        """Write data to stream and queue complete lines for logging.

        Buffers partial lines until a newline is received, then queues
        each complete line as a single entry.
        """
        self.stream.write(data)

        with self._buffer_lock:
            self._line_buffer += data
            while "\n" in self._line_buffer:
                line, self._line_buffer = self._line_buffer.split("\n", 1)
                self._log_data_queue.put_nowait(line + "\n")

    def flush_buffer(self) -> None:
        """Flush any remaining buffered content to the queue."""
        with self._buffer_lock:
            if self._line_buffer:
                self._log_data_queue.put_nowait(self._line_buffer)
                self._line_buffer = ""

    def __getattr__(self, attr: str) -> object:
        return getattr(self.stream, attr)

    def close(self) -> None:
        if self.enabled:
            self._logging_thread.interrupt()
        self.enabled = False
        self.flush_buffer()
        self._log_data_queue.put_nowait(None)
        self._logging_thread.join()

    class ReportingThread(Daemon):
        def __init__(self, logger: StdStreamCaptureLogger, name: str):
            super().__init__(sleep_time=0, name=name)
            self._logger = logger

        @Daemon.ConnectionRetryWrapper(kill_message="Killing Neptune STD capturing thread.")
        def work(self) -> None:
            while True:
                data = self._logger._log_data_queue.get()
                if data is None:
                    break
                self._logger._logger.log(data)


class StdoutCaptureLogger(StdStreamCaptureLogger):
    def __init__(self, container: MetadataContainer, attribute_name: str) -> None:
        super().__init__(container, attribute_name, sys.stdout)
        sys.stdout = self

    def close(self) -> None:
        sys.stdout = self.stream
        super().close()


class StderrCaptureLogger(StdStreamCaptureLogger):
    def __init__(self, container: MetadataContainer, attribute_name: str) -> None:
        super().__init__(container, attribute_name, sys.stderr)
        sys.stderr = self

    def close(self, wait_for_all_logs: bool = True) -> None:
        sys.stderr = self.stream
        super().close()
