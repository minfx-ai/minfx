#
# Copyright (c) 2023, Neptune Labs Sp. z o.o.
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

__all__ = ["__version__", "version"]


from packaging.version import parse

from minfx import __version__ as minfx_version

# The neptune_v2 code is bundled inside minfx.
# Use the minfx package version directly.
# For dev versions (0.0.0.dev0) or unknown, use a reasonable default
# that passes server version checks.
_FALLBACK_VERSION = "1.0.0"

if minfx_version in ("unknown", "0.0.0.dev0"):
    __version__ = _FALLBACK_VERSION
else:
    __version__ = minfx_version

version = parse(__version__)
