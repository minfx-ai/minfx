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

from abc import (
    ABCMeta,
    abstractmethod,
)
from dataclasses import dataclass
import os
from pathlib import Path
from pprint import pformat
import stat
import time
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Generator,
)

import six

from minfx.neptune_v2.internal.utils.logger import get_logger

if TYPE_CHECKING:
    import io
    from io import BytesIO

_logger = get_logger()


@dataclass
class AttributeUploadConfiguration:
    chunk_size: int


class UploadEntry:
    def __init__(self, source: str | BytesIO, target_path: str):
        self.source = source
        self.target_path = target_path

    def length(self) -> int:
        if self.is_stream():
            return self.source.getbuffer().nbytes
        return Path(self.source).stat().st_size

    def get_stream(self) -> BinaryIO | io.BytesIO:
        if self.is_stream():
            return self.source
        return Path(self.source).open("rb")

    def get_permissions(self) -> str:
        if self.is_stream():
            return "----------"
        return self.permissions_to_unix_string(self.source)

    @classmethod
    def permissions_to_unix_string(cls, path: str) -> str:
        st = 0
        if Path(path).exists():
            st = os.lstat(path).st_mode
        is_dir = "d" if stat.S_ISDIR(st) else "-"
        dic = {
            "7": "rwx",
            "6": "rw-",
            "5": "r-x",
            "4": "r--",
            "3": "-wx",
            "2": "-w-",
            "1": "--x",
            "0": "---",
        }
        perm = (f"{st:03o}")[-3:]
        return is_dir + "".join(dic.get(x, x) for x in perm)

    def __eq__(self, other: object) -> bool:
        """Returns true if both objects are equal."""
        return self.__dict__ == other.__dict__

    def __ne__(self, other: object) -> bool:
        """Returns true if both objects are not equal."""
        return not self == other

    def __hash__(self) -> int:
        """Returns the hash of source and target path."""
        return hash((self.source, self.target_path))

    def to_str(self) -> str:
        """Returns the string representation of the model."""
        return pformat(self.__dict__)

    def __repr__(self) -> str:
        """For `print` and `pprint`."""
        return self.to_str()

    def is_stream(self) -> bool:
        return hasattr(self.source, "read")


class UploadPackage:
    def __init__(self) -> None:
        self.items: list[UploadEntry] = []
        self.size: int = 0
        self.len: int = 0

    def reset(self) -> None:
        self.items = []
        self.size = 0
        self.len = 0

    def update(self, entry: UploadEntry, size: int) -> None:
        self.items.append(entry)
        self.size += size
        self.len += 1

    def is_empty(self) -> bool:
        return self.len == 0

    def __eq__(self, other: object) -> bool:
        """Returns true if both objects are equal."""
        return self.__dict__ == other.__dict__

    def __ne__(self, other: object) -> bool:
        """Returns true if both objects are not equal."""
        return not self == other

    def __hash__(self) -> int:
        return hash((tuple(self.items), self.size, self.len))

    def to_str(self) -> str:
        """Returns the string representation of the model."""
        return pformat(self.__dict__)

    def __repr__(self) -> str:
        """For `print` and `pprint`."""
        return self.to_str()


@six.add_metaclass(ABCMeta)
class ProgressIndicator:
    @abstractmethod
    def progress(self, steps: int) -> None:
        pass

    @abstractmethod
    def complete(self) -> None:
        pass


class LoggingProgressIndicator(ProgressIndicator):
    def __init__(self, total: int, frequency: int = 10) -> None:
        self.current = 0
        self.total = total
        self.last_warning = time.time()
        self.frequency = frequency
        _logger.warning(
            "You are sending %dMB of source code to Neptune. "
            "It is pretty uncommon - please make sure it's what you wanted.",
            self.total / (1024 * 1024),
        )

    def progress(self, steps: int) -> None:
        self.current += steps
        if time.time() - self.last_warning > self.frequency:
            _logger.warning(
                "%d MB / %d MB (%d%%) of source code was sent to Neptune.",
                self.current / (1024 * 1024),
                self.total / (1024 * 1024),
                100 * self.current / self.total,
            )
            self.last_warning = time.time()

    def complete(self) -> None:
        _logger.warning(
            "%d MB (100%%) of source code was sent to Neptune.",
            self.total / (1024 * 1024),
        )


class SilentProgressIndicator(ProgressIndicator):
    def __init__(self) -> None:
        pass

    def progress(self, steps: int) -> None:
        pass

    def complete(self) -> None:
        pass


def scan_unique_upload_entries(upload_entries: set[UploadEntry]) -> set[UploadEntry]:
    """Returns upload entries for all files that could be found for given upload entries.
    In case of directory as upload entry, files we be taken from all subdirectories recursively.
    Any duplicated entries are removed.
    """
    walked_entries = set()
    for entry in upload_entries:
        if entry.is_stream() or not Path(entry.source).is_dir():
            walked_entries.add(entry)
        else:
            for root, _, files in os.walk(entry.source):
                path_relative_to_entry_source = os.path.relpath(root, entry.source)
                target_root = str((Path(entry.target_path) / path_relative_to_entry_source).as_posix())
                for filename in files:
                    walked_entries.add(
                        UploadEntry(
                            str(Path(root) / filename),
                            str(Path(target_root) / filename),
                        )
                    )

    return walked_entries


def split_upload_files(
    upload_entries: set[UploadEntry],
    upload_configuration: AttributeUploadConfiguration,
    max_files: int = 500,
) -> Generator[UploadPackage, None, None]:
    current_package = UploadPackage()

    for entry in upload_entries:
        if entry.is_stream():
            if current_package.len > 0:
                yield current_package
                current_package.reset()
            current_package.update(entry, 0)
            yield current_package
            current_package.reset()
        else:
            size = Path(entry.source).stat().st_size
            if (
                size + current_package.size > upload_configuration.chunk_size or current_package.len > max_files
            ) and not current_package.is_empty():
                yield current_package
                current_package.reset()
            current_package.update(entry, size)

    yield current_package


def normalize_file_name(name: str) -> str:
    return name.replace(os.sep, "/")
