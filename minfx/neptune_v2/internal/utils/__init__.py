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
    "as_list",
    "base64_decode",
    "base64_encode",
    "does_paths_share_common_drive",
    "get_absolute_paths",
    "get_common_root",
    "is_bool",
    "is_collection",
    "is_dict_like",
    "is_float",
    "is_float_like",
    "is_int",
    "is_ipython",
    "is_stream",
    "is_string",
    "is_string_like",
    "is_stringify_value",
    "replace_patch_version",
    "verify_collection_type",
    "verify_optional_callable",
    "verify_type",
    "verify_value",
]

import base64
from glob import glob
from io import IOBase
import os
from pathlib import Path
from typing import (
    Iterable,
    Mapping,
    TypeVar,
)

from minfx.neptune_v2.internal.types.stringify_value import StringifyValue
from minfx.neptune_v2.internal.utils.logger import get_logger

T = TypeVar("T")

_logger = get_logger()


def replace_patch_version(version: str) -> str:
    return version[: version.index(".", version.index(".") + 1)] + ".0"


def verify_type(var_name: str, var: object, expected_type: type | tuple[type, ...]) -> None:
    try:
        if isinstance(expected_type, tuple):
            type_name = " or ".join(get_type_name(t) for t in expected_type)
        else:
            type_name = get_type_name(expected_type)
    except Exception as e:
        # Just to be sure that nothing weird will be raised here
        raise TypeError(f"Incorrect type of {var_name}") from e

    if not isinstance(var, expected_type):
        raise TypeError(f"{var_name} must be a {type_name} (was {type(var)})")

    if isinstance(var, IOBase) and not hasattr(var, "read"):
        raise TypeError(f"{var_name} is a stream, which does not implement read method")


def verify_value(var_name: str, var: T, expected_values: Iterable[T]) -> None:
    if var not in expected_values:
        raise ValueError(f"{var_name} must be one of {expected_values} (was `{var}`)")


def is_stream(var: object) -> bool:
    return isinstance(var, IOBase) and hasattr(var, "read")


def is_bool(var: object) -> bool:
    return isinstance(var, bool)


def is_int(var: object) -> bool:
    return isinstance(var, int)


def is_float(var: object) -> bool:
    return isinstance(var, (float, int))


def is_string(var: object) -> bool:
    return isinstance(var, str)


def is_float_like(var: object) -> bool:
    try:
        _ = float(var)
        return True
    except (ValueError, TypeError):
        return False


def is_dict_like(var: object) -> bool:
    return isinstance(var, (dict, Mapping))


def is_string_like(var: object) -> bool:
    try:
        _ = str(var)
        return True
    except ValueError:
        return False


def is_stringify_value(var: object) -> bool:
    return isinstance(var, StringifyValue)


def get_type_name(_type: type | tuple[type, ...]) -> str:
    return _type.__name__ if hasattr(_type, "__name__") else str(_type)


def verify_collection_type(var_name: str, var: object, expected_type: type | tuple[type, ...]) -> None:
    verify_type(var_name, var, (list, set, tuple))
    for value in var:
        verify_type(f"elements of collection '{var_name}'", value, expected_type)


def verify_optional_callable(var_name: str, var: object) -> None:
    if var and not callable(var):
        raise TypeError(f"{var_name} must be a callable (was {type(var)})")


def is_collection(var: object) -> bool:
    return isinstance(var, (list, set, tuple))


def base64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def base64_decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def get_absolute_paths(file_globs: Iterable[str]) -> list[str]:
    expanded_paths: set[str] = set()
    for file_glob in file_globs:
        expanded_paths |= set(glob(file_glob, recursive=True))
    return [str(Path(expanded_file).resolve()) for expanded_file in expanded_paths]


def get_common_root(absolute_paths: list[str]) -> str | None:
    try:
        common_root = os.path.commonpath(absolute_paths)
        common_root_path = Path(common_root)
        if common_root_path.is_file():
            common_root = str(common_root_path.parent)
        cwd = str(Path.cwd())
        if common_root.startswith(cwd + os.sep):
            common_root = cwd
        return common_root
    except ValueError:
        return None


def does_paths_share_common_drive(paths: list[str]) -> bool:
    return len({os.path.splitdrive(path)[0] for path in paths}) == 1


def is_ipython() -> bool:
    try:
        import IPython

        ipython = IPython.core.getipython.get_ipython()
        return ipython is not None
    except ImportError:
        return False


def as_list(name: str, value: str | Iterable[str] | None) -> Iterable[str]:
    verify_type(name, value, (type(None), str, Iterable))

    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    verify_collection_type(name, value, str)

    return value
