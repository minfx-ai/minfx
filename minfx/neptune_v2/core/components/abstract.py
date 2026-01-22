#
# Copyright (c) 2024, Neptune Labs Sp. z o.o.
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
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
)

from typing_extensions import Self

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


class AutoCloseable(ABC):
    def __enter__(self) -> Self:
        return self

    @abstractmethod
    def close(self) -> None: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class Resource(AutoCloseable):
    @abstractmethod
    def cleanup(self) -> None: ...

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.flush()

    @property
    @abstractmethod
    def data_path(self) -> Path: ...


class WithResources(Resource):
    @property
    @abstractmethod
    def resources(self) -> tuple[Resource, ...]: ...

    def flush(self) -> None:
        for resource in self.resources:
            resource.flush()

    def close(self) -> None:
        for resource in self.resources:
            resource.close()

    def cleanup(self) -> None:
        for resource in self.resources:
            resource.cleanup()
