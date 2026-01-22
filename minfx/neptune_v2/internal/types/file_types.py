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
    "FileComposite",
    "FileComposite",
    "InMemoryComposite",
    "LocalFileComposite",
    "StreamComposite",
]

import abc
import enum
from functools import wraps
import io
from io import IOBase
from pathlib import Path
from typing import (
    Any,
    Callable,
    TypeVar,
)

R = TypeVar("R")

from minfx.neptune_v2.common.exceptions import NeptuneException
from minfx.neptune_v2.exceptions import StreamAlreadyUsedException
from minfx.neptune_v2.internal.utils import verify_type


class FileType(enum.Enum):
    LOCAL_FILE = "LOCAL_FILE"
    IN_MEMORY = "IN_MEMORY"
    STREAM = "STREAM"


class FileComposite(abc.ABC):
    """Composite class defining behaviour of neptune.types.atoms.file.File."""

    file_type: FileType = None

    def __init__(self, extension: str):
        verify_type("extension", extension, str)
        self._extension = extension

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def path(self) -> str:
        raise NeptuneException(f"`path` attribute is not supported for {self.file_type}")

    @property
    def content(self) -> bytes:
        raise NeptuneException(f"`content` attribute is not supported for {self.file_type}")

    def save(self, path: list[str]):
        raise NeptuneException(f"`save` method is not supported for {self.file_type}")


class LocalFileComposite(FileComposite):
    file_type = FileType.LOCAL_FILE

    def __init__(self, path: str, extension: str | None = None):
        try:
            ext = Path(path).suffix
            ext = ext[1:] if ext else ""
        except ValueError:
            ext = ""
        super().__init__(extension or ext)

        self._path = path

    @property
    def path(self) -> str:
        return self._path

    def __str__(self) -> str:
        return f"File(path={self.path})"


class InMemoryComposite(FileComposite):
    file_type = FileType.IN_MEMORY

    def __init__(self, content: str | bytes, extension: str | None = None):
        if isinstance(content, str):
            ext = "txt"
            content = content.encode("utf-8")
        else:
            ext = "bin"
        super().__init__(extension or ext)

        self._content = content

    @property
    def content(self) -> bytes:
        return self._content

    def save(self, path: list[str]):
        with Path(path).open("wb") as f:
            f.write(self._content)

    def __str__(self) -> str:
        return "File(content=...)"


def read_once(f: Callable[..., R]) -> Callable[..., R]:
    """Decorator for validating read once on STREAM objects."""

    @wraps(f)
    def func(self: StreamComposite, *args: Any, **kwargs: Any) -> R:
        if self._stream_read:
            raise StreamAlreadyUsedException
        self._stream_read = True
        return f(self, *args, **kwargs)

    return func


class StreamComposite(FileComposite):
    file_type = FileType.STREAM

    def __init__(self, stream: IOBase, seek: int | None = 0, extension: str | None = None):
        verify_type("stream", stream, (IOBase, type(None)))
        verify_type("extension", extension, (str, type(None)))

        if seek is not None and stream.seekable():
            stream.seek(seek)
        if extension is None:
            extension = "txt" if isinstance(stream, io.TextIOBase) else "bin"
        super().__init__(extension)

        self._stream = stream
        self._stream_read = False

    @property
    @read_once
    def content(self) -> bytes:
        val = self._stream.read()
        if isinstance(self._stream, io.TextIOBase):
            val = val.encode()
        return val

    @read_once
    def save(self, path: list[str]):
        with Path(path).open("wb") as f:
            buffer_ = self._stream.read(io.DEFAULT_BUFFER_SIZE)
            while buffer_:
                # TODO: replace with Walrus Operator once python3.7 support is dropped
                if isinstance(self._stream, io.TextIOBase):
                    buffer_ = buffer_.encode()
                f.write(buffer_)
                buffer_ = self._stream.read(io.DEFAULT_BUFFER_SIZE)

    def __str__(self) -> str:
        return f"File(stream={self._stream})"
