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

__all__ = ["BackgroundJob"]

import abc
from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from minfx.neptune_v2.metadata_containers import MetadataContainer


class BackgroundJob:
    @abc.abstractmethod
    def start(self, container: MetadataContainer):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def join(self, seconds: float | None = None):
        pass

    @abc.abstractmethod
    def pause(self):
        pass

    @abc.abstractmethod
    def resume(self):
        pass
