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

__all__ = ["NullProgressBar", "ProgressBarCallback", "ProgressBarType", "TqdmProgressBar"]

import abc
import contextlib
from typing import (
    TYPE_CHECKING,
    Type,
    Union,
)

from typing_extensions import (
    Self,
    TypeAlias,
)

from minfx.neptune_v2.internal.utils.runningmode import (
    in_interactive,
    in_notebook,
)

if TYPE_CHECKING:
    from types import TracebackType


class ProgressBarCallback(contextlib.AbstractContextManager):
    """Abstract base class for progress bar callbacks.

    You can use this class to implement your own progress bar callback that will be invoked in table fetching methods:

    - `fetch_runs_table()`
    - `fetch_models_table()`
    - `fetch_model_versions_table()`

    Example using `click`:
        >>> from typing import Optional, Type
        >>> from types import TracebackType
        >>> from minfx.neptune_v2.progress_bar import ProgressBarCallback
        >>> class ClickProgressBar(ProgressBarCallback):
        ...     def __init__(self, *, description: Optional[str] = None, **_: object) -> None:
        ...         super().__init__()
        ...         from click import progressbar
        ...
        ...         self._progress_bar = progressbar(iterable=None, length=1, label=description)
        ...
        ...     def update(self, *, by: int, total: Optional[int] = None) -> None:
        ...         if total:
        ...             self._progress_bar.length = total
        ...         self._progress_bar.update(by)
        ...
        ...     def __enter__(self) -> "ClickProgressBar":
        ...         self._progress_bar.__enter__()
        ...         return self
        ...
        ...     def __exit__(
        ...         self,
        ...         exc_type: Optional[Type[BaseException]],
        ...         exc_val: Optional[BaseException],
        ...         exc_tb: Optional[TracebackType],
        ...     ) -> None:
        ...         self._progress_bar.__exit__(exc_type, exc_val, exc_tb)
        >>> from minfx.neptune_v2 import init_project
        >>> with init_project() as project:
        ...     project.fetch_runs_table(progress_bar=ClickProgressBar)
        ...     project.fetch_models_table(progress_bar=ClickProgressBar)

        IMPORTANT: Pass a type, not an instance to the `progress_bar` argument.
        That is, `ClickProgressBar`, not `ClickProgressBar()`.
    """

    def __init__(self, *args: object, **kwargs: object) -> None: ...

    @abc.abstractmethod
    def update(self, *, by: int, total: int | None = None) -> None: ...


ProgressBarType: TypeAlias = Union[bool, Type[ProgressBarCallback]]


class NullProgressBar(ProgressBarCallback):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def update(self, *, by: int, total: int | None = None) -> None:
        pass


class TqdmProgressBar(ProgressBarCallback):
    def __init__(
        self,
        *args: object,
        description: str | None = None,
        unit: str | None = None,
        unit_scale: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)
        interactive = in_interactive() or in_notebook()

        if interactive:
            from tqdm.notebook import tqdm
        else:
            from tqdm import tqdm  # type: ignore[import-untyped]

        unit = unit if unit else ""

        self._progress_bar = tqdm(desc=description, unit=unit, unit_scale=unit_scale, **kwargs)

    def __enter__(self) -> Self:
        self._progress_bar.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._progress_bar.__exit__(exc_type, exc_val, exc_tb)

    def update(self, *, by: int, total: int | None = None) -> None:
        if total:
            self._progress_bar.total = total
        self._progress_bar.update(by)
