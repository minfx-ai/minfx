#
# Copyright (c) 2026, minfx.ai
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
"""
Neptune SDK compatibility detection.

This module provides utilities to detect when users are passing Neptune SDK types
instead of the minfx equivalents, and raises helpful TypeError messages or warnings.
"""

from __future__ import annotations

__all__ = [
    "check_not_neptune_sdk_artifact",
    "check_not_neptune_sdk_atom",
    "check_not_neptune_sdk_file",
    "check_not_neptune_sdk_file_series",
    "check_not_neptune_sdk_file_set",
    "check_not_neptune_sdk_namespace",
    "check_not_neptune_sdk_run",
    "check_not_neptune_sdk_stringify_value",
    "check_not_neptune_sdk_string_set",
    "is_neptune_sdk_artifact",
    "is_neptune_sdk_atom",
    "is_neptune_sdk_file",
    "is_neptune_sdk_file_series",
    "is_neptune_sdk_file_set",
    "is_neptune_sdk_namespace",
    "is_neptune_sdk_run",
    "is_neptune_sdk_series",
    "is_neptune_sdk_stringify_value",
    "is_neptune_sdk_string_set",
    "warn_neptune_sdk_file_series",
    "warn_neptune_sdk_series",
]


def _get_module_path(obj: object) -> str:
    """Get the full module path of an object's class."""
    cls = type(obj)
    module = getattr(cls, "__module__", "")
    name = getattr(cls, "__name__", "")
    return f"{module}.{name}" if module else name


def _is_neptune_sdk_type(value: object, class_name: str) -> bool:
    """Check if value is a Neptune SDK type with the given class name.

    Args:
        value: The value to check.
        class_name: The expected class name (e.g., "File", "FloatSeries").

    Returns:
        True if value is a Neptune SDK type with the given name, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune = module_path.startswith("neptune.") and type_name == class_name
    is_minfx = "minfx" in module_path
    return is_neptune and not is_minfx


# =============================================================================
# File detection
# =============================================================================


def is_neptune_sdk_file(value: object) -> bool:
    """Check if value is a Neptune SDK File type (not minfx).

    Neptune SDK's File class lives in neptune.types.atoms.file.File.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's File type, False otherwise.
    """
    module_path = _get_module_path(value)
    # Check for Neptune SDK File type
    # neptune.types.atoms.file.File or neptune.types.File (re-exported)
    is_neptune_file = "neptune.types.atoms.file.File" in module_path or (
        module_path.startswith("neptune.types") and type(value).__name__ == "File"
    )
    # Make sure it's not our minfx File
    is_minfx_file = "minfx" in module_path
    return is_neptune_file and not is_minfx_file


def check_not_neptune_sdk_file(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK File type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's File type.
    """
    if is_neptune_sdk_file(value):
        raise TypeError(
            "You are using Neptune SDK's File type (neptune.types.File). "
            "Please use minfx's File type instead:\n"
            "  from minfx.neptune_v2.types import File\n"
            "  run['file'] = File.from_path('path/to/file')"
        )


# =============================================================================
# StringifyValue detection
# =============================================================================


def is_neptune_sdk_stringify_value(value: object) -> bool:
    """Check if value is a Neptune SDK StringifyValue type (not minfx).

    Neptune SDK's StringifyValue lives in neptune.internal.types.stringify_value.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's StringifyValue type, False otherwise.
    """
    module_path = _get_module_path(value)
    # Check for Neptune SDK StringifyValue type
    is_neptune_stringify = "neptune.internal.types.stringify_value.StringifyValue" in module_path or (
        module_path.startswith("neptune.") and type(value).__name__ == "StringifyValue"
    )
    # Make sure it's not our minfx StringifyValue
    is_minfx_stringify = "minfx" in module_path
    return is_neptune_stringify and not is_minfx_stringify


def check_not_neptune_sdk_stringify_value(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK StringifyValue type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's StringifyValue type.
    """
    if is_neptune_sdk_stringify_value(value):
        raise TypeError(
            "You are using Neptune SDK's stringify_unsupported() function. "
            "Please use minfx's version instead:\n"
            "  from minfx.neptune_v2.utils import stringify_unsupported\n"
            "  run['value'] = stringify_unsupported(my_object)"
        )


# =============================================================================
# Series detection (FloatSeries, StringSeries)
# =============================================================================


def is_neptune_sdk_series(value: object) -> bool:
    """Check if value is a Neptune SDK series type (FloatSeries or StringSeries).

    Neptune SDK's series types live in neptune.types.series.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's series type, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune_series = module_path.startswith("neptune.") and type_name in ("FloatSeries", "StringSeries")
    is_minfx = "minfx" in module_path
    return is_neptune_series and not is_minfx


def warn_neptune_sdk_series(value: object) -> None:
    """Emit a deprecation warning if value is a Neptune SDK series type.

    Unlike File/StringifyValue, we allow series to be used but warn users
    to migrate to minfx types for better compatibility.

    Args:
        value: The value to check.
    """
    if is_neptune_sdk_series(value):
        from minfx.neptune_v2.common.warnings import warn_once

        type_name = type(value).__name__
        warn_once(
            f"You are using Neptune SDK's {type_name} type. "
            f"Consider using minfx's {type_name} instead for better compatibility:\n"
            f"  from minfx.neptune_v2.types import {type_name}\n"
            f"  run['series'] = {type_name}(values=[1.0, 2.0, 3.0])"
        )


# =============================================================================
# Run detection
# =============================================================================


def is_neptune_sdk_run(value: object) -> bool:
    """Check if value is a Neptune SDK Run type (not minfx).

    Neptune SDK's Run class lives in neptune.metadata_containers.run.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's Run type, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune_run = module_path.startswith("neptune.") and type_name == "Run"
    is_minfx = "minfx" in module_path
    return is_neptune_run and not is_minfx


def check_not_neptune_sdk_run(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK Run type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's Run type.
    """
    if is_neptune_sdk_run(value):
        raise TypeError(
            "You are using Neptune SDK's Run object. "
            "Please use minfx's Run instead:\n"
            "  from minfx.neptune_v2 import Run\n"
            "  run = Run(project='workspace/project')"
        )


# =============================================================================
# Namespace detection
# =============================================================================


def is_neptune_sdk_namespace(value: object) -> bool:
    """Check if value is a Neptune SDK Namespace type (not minfx).

    Neptune SDK's Namespace class lives in neptune.types.namespace.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's Namespace type, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune_namespace = module_path.startswith("neptune.") and type_name == "Namespace"
    is_minfx = "minfx" in module_path
    return is_neptune_namespace and not is_minfx


def check_not_neptune_sdk_namespace(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK Namespace type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's Namespace type.
    """
    if is_neptune_sdk_namespace(value):
        raise TypeError(
            "You are using Neptune SDK's Namespace type. "
            "Please use minfx's Namespace or a plain dict instead:\n"
            "  from minfx.neptune_v2.types import Namespace\n"
            "  run['params'] = Namespace({'lr': 0.01, 'epochs': 10})\n"
            "  # Or simply use a dict:\n"
            "  run['params'] = {'lr': 0.01, 'epochs': 10}"
        )


# =============================================================================
# Artifact detection
# =============================================================================


def is_neptune_sdk_artifact(value: object) -> bool:
    """Check if value is a Neptune SDK Artifact type (not minfx).

    Neptune SDK's Artifact class lives in neptune.types.atoms.artifact.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's Artifact type, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune_artifact = module_path.startswith("neptune.") and type_name == "Artifact"
    is_minfx = "minfx" in module_path
    return is_neptune_artifact and not is_minfx


def check_not_neptune_sdk_artifact(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK Artifact type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's Artifact type.
    """
    if is_neptune_sdk_artifact(value):
        raise TypeError(
            "You are using Neptune SDK's Artifact type. "
            "Please use minfx's artifact tracking instead:\n"
            "  run['artifact'].track_files('path/to/files')"
        )


# =============================================================================
# Atom type detection (Boolean, Integer, Float, String, Datetime)
# =============================================================================

_NEPTUNE_ATOM_TYPES = frozenset({"Boolean", "Integer", "Float", "String", "Datetime"})

_ATOM_TYPE_SUGGESTIONS = {
    "Boolean": "Use a plain Python bool instead: run['flag'] = True",
    "Integer": "Use a plain Python int instead: run['count'] = 42",
    "Float": "Use a plain Python float instead: run['value'] = 3.14",
    "String": "Use a plain Python str instead: run['name'] = 'experiment'",
    "Datetime": "Use datetime.datetime or import from minfx:\n"
    "  from datetime import datetime\n"
    "  run['timestamp'] = datetime.now()",
}


def is_neptune_sdk_atom(value: object) -> bool:
    """Check if value is a Neptune SDK atom type (Boolean, Integer, Float, String, Datetime).

    Neptune SDK's atom types live in neptune.types.atoms.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's atom type, False otherwise.
    """
    module_path = _get_module_path(value)
    type_name = type(value).__name__
    is_neptune_atom = module_path.startswith("neptune.") and type_name in _NEPTUNE_ATOM_TYPES
    is_minfx = "minfx" in module_path
    return is_neptune_atom and not is_minfx


def check_not_neptune_sdk_atom(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK atom type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's atom type.
    """
    if is_neptune_sdk_atom(value):
        type_name = type(value).__name__
        suggestion = _ATOM_TYPE_SUGGESTIONS.get(type_name, "Use plain Python types instead.")
        raise TypeError(
            f"You are using Neptune SDK's {type_name} type (neptune.types.{type_name}). "
            f"This is not needed with minfx - values are automatically wrapped.\n"
            f"{suggestion}"
        )


# =============================================================================
# StringSet detection
# =============================================================================


def is_neptune_sdk_string_set(value: object) -> bool:
    """Check if value is a Neptune SDK StringSet type (not minfx).

    Neptune SDK's StringSet class lives in neptune.types.sets.string_set.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's StringSet type, False otherwise.
    """
    return _is_neptune_sdk_type(value, "StringSet")


def check_not_neptune_sdk_string_set(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK StringSet type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's StringSet type.
    """
    if is_neptune_sdk_string_set(value):
        raise TypeError(
            "You are using Neptune SDK's StringSet type (neptune.types.StringSet). "
            "Please use minfx's StringSet or a plain set/list of strings instead:\n"
            "  from minfx.neptune_v2.types import StringSet\n"
            "  run['tags'] = StringSet(values=['tag1', 'tag2'])\n"
            "  # Or simply use a set/list:\n"
            "  run['tags'].add(['tag1', 'tag2'])"
        )


# =============================================================================
# FileSet detection
# =============================================================================


def is_neptune_sdk_file_set(value: object) -> bool:
    """Check if value is a Neptune SDK FileSet type (not minfx).

    Neptune SDK's FileSet class lives in neptune.types.file_set.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's FileSet type, False otherwise.
    """
    return _is_neptune_sdk_type(value, "FileSet")


def check_not_neptune_sdk_file_set(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK FileSet type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's FileSet type.
    """
    if is_neptune_sdk_file_set(value):
        raise TypeError(
            "You are using Neptune SDK's FileSet type (neptune.types.FileSet). "
            "Please use minfx's FileSet or upload files directly instead:\n"
            "  from minfx.neptune_v2.types import FileSet\n"
            "  run['files'] = FileSet(file_globs=['*.py', 'data/*.csv'])\n"
            "  # Or use upload_files directly:\n"
            "  run['files'].upload_files(['file1.py', 'file2.py'])"
        )


# =============================================================================
# FileSeries detection
# =============================================================================


def is_neptune_sdk_file_series(value: object) -> bool:
    """Check if value is a Neptune SDK FileSeries type (not minfx).

    Neptune SDK's FileSeries class lives in neptune.types.series.file_series.
    We detect it by checking the module path to avoid importing neptune.

    Args:
        value: The value to check.

    Returns:
        True if value is Neptune SDK's FileSeries type, False otherwise.
    """
    return _is_neptune_sdk_type(value, "FileSeries")


def warn_neptune_sdk_file_series(value: object) -> None:
    """Emit a deprecation warning if value is a Neptune SDK FileSeries type.

    Unlike File/StringifyValue, we allow FileSeries to be used but warn users
    to migrate to minfx types for better compatibility.

    Args:
        value: The value to check.
    """
    if is_neptune_sdk_file_series(value):
        from minfx.neptune_v2.common.warnings import warn_once

        warn_once(
            "You are using Neptune SDK's FileSeries type. "
            "Consider using minfx's FileSeries instead for better compatibility:\n"
            "  from minfx.neptune_v2.types import FileSeries\n"
            "  run['images'] = FileSeries(values=[image1, image2])"
        )


def check_not_neptune_sdk_file_series(value: object) -> None:
    """Raise TypeError if value is a Neptune SDK FileSeries type.

    Args:
        value: The value to check.

    Raises:
        TypeError: If value is Neptune SDK's FileSeries type.
    """
    if is_neptune_sdk_file_series(value):
        raise TypeError(
            "You are using Neptune SDK's FileSeries type (neptune.types.FileSeries). "
            "Please use minfx's FileSeries instead:\n"
            "  from minfx.neptune_v2.types import FileSeries\n"
            "  run['images'] = FileSeries(values=[image1, image2])"
        )
