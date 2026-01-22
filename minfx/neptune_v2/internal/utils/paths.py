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

__all__ = ["join_paths", "parse_path", "path_to_str"]


def _remove_empty_paths(paths: list[str]) -> list[str]:
    return list(filter(bool, paths))


def parse_path(path: str) -> list[str]:
    return _remove_empty_paths(str(path).split("/"))


def path_to_str(path: list[str]) -> str:
    return "/".join(_remove_empty_paths(path))


def join_paths(*paths: str) -> str:
    return "/".join(_remove_empty_paths([str(path) for path in paths]))
