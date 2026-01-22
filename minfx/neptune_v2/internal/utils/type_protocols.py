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
"""Protocol classes for duck-typed library objects.

These protocols enable proper typing for objects from optional dependencies
like matplotlib, plotly, seaborn, etc. without requiring those packages to be installed.
"""

from __future__ import annotations

__all__ = [
    "AltairChartLike",
    "BokehFigureLike",
    "MatplotlibAxesLike",
    "MatplotlibFigureLike",
    "NumpyArrayLike",
    "PILImageLike",
    "PlotlyFigureLike",
    "SeabornGridLike",
    "TensorflowTensorLike",
    "TorchTensorLike",
]

from typing import (
    TYPE_CHECKING,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from io import IOBase


@runtime_checkable
class NumpyArrayLike(Protocol):
    """Protocol for numpy ndarray-like objects."""

    @property
    def shape(self) -> tuple[int, ...]: ...
    def copy(self) -> NumpyArrayLike: ...
    def min(self) -> float: ...
    def max(self) -> float: ...
    def astype(self, dtype: object) -> NumpyArrayLike: ...


@runtime_checkable
class PILImageLike(Protocol):
    """Protocol for PIL Image-like objects."""

    def save(self, fp: str | IOBase, format: str | None = None) -> None: ...


@runtime_checkable
class MatplotlibFigureLike(Protocol):
    """Protocol for matplotlib Figure-like objects."""

    def savefig(
        self,
        fname: str | IOBase,
        *,
        format: str | None = None,
        bbox_inches: str | None = None,
    ) -> None: ...


@runtime_checkable
class MatplotlibAxesLike(Protocol):
    """Protocol for matplotlib Axes-like objects."""

    @property
    def figure(self) -> MatplotlibFigureLike: ...


@runtime_checkable
class PlotlyFigureLike(Protocol):
    """Protocol for Plotly Figure-like objects."""

    def write_html(
        self,
        file: str | IOBase,
        *,
        include_plotlyjs: bool = True,
    ) -> None: ...


@runtime_checkable
class AltairChartLike(Protocol):
    """Protocol for Altair Chart-like objects."""

    def save(self, fp: str | IOBase, format: str | None = None) -> None: ...


@runtime_checkable
class BokehFigureLike(Protocol):
    """Protocol for Bokeh Figure-like objects.

    Bokeh figures are identified by module name check, not specific methods.
    """


@runtime_checkable
class SeabornGridLike(Protocol):
    """Protocol for Seaborn grid-like objects (FacetGrid, PairGrid, JointGrid)."""

    @property
    def figure(self) -> MatplotlibFigureLike: ...


@runtime_checkable
class TorchTensorLike(Protocol):
    """Protocol for PyTorch Tensor-like objects."""

    def detach(self) -> TorchTensorLike: ...
    def numpy(self) -> NumpyArrayLike: ...


@runtime_checkable
class TensorflowTensorLike(Protocol):
    """Protocol for TensorFlow Tensor-like objects."""

    def numpy(self) -> NumpyArrayLike: ...
