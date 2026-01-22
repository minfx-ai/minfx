#
# Copyright (c) 2019, Neptune Labs Sp. z o.o.
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

from typing import TYPE_CHECKING

try:
    import psutil

    PSUTIL_INSTALLED = True
except ImportError:
    PSUTIL_INSTALLED = False

if TYPE_CHECKING:
    from psutil._common import svmem


class SystemMonitor:
    @staticmethod
    def cpu_count() -> int | None:
        return psutil.cpu_count()

    @staticmethod
    def cpu_percent() -> float:
        return psutil.cpu_percent()

    @staticmethod
    def virtual_memory() -> svmem:
        return psutil.virtual_memory()
