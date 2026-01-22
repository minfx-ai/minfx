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

__all__ = ("LazyOperationProcessorWrapper",)

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    TypeVar,
)

from minfx.neptune_v2.core.components.abstract import Resource
from minfx.neptune_v2.internal.operation_processors.operation_processor import OperationProcessor

if TYPE_CHECKING:
    from pathlib import Path

    from minfx.neptune_v2.core.components.operation_storage import OperationStorage
    from minfx.neptune_v2.internal.operation import Operation

RT = TypeVar("RT")


def trigger_evaluation(method: Callable[..., RT]) -> Callable[..., RT]:
    def _wrapper(self: LazyOperationProcessorWrapper, *args: Any, **kwargs: Any) -> RT:
        self.evaluate()
        return method(self, *args, **kwargs)

    return _wrapper


def noop_if_not_evaluated(method: Callable[..., RT]) -> Callable[..., RT | None]:
    def _wrapper(self: LazyOperationProcessorWrapper, *args: Any, **kwargs: Any) -> RT | None:
        if self.is_evaluated:
            return method(self, *args, **kwargs)
        return None

    return _wrapper


def noop_if_evaluated(method: Callable[..., RT]) -> Callable[..., RT | None]:
    def _wrapper(self: LazyOperationProcessorWrapper, *args: Any, **kwargs: Any) -> RT | None:
        if not self.is_evaluated:
            return method(self, *args, **kwargs)
        return None

    return _wrapper


class LazyOperationProcessorWrapper(OperationProcessor):
    def __init__(
        self,
        operation_processor_getter: Callable[[], OperationProcessor],
        post_trigger_side_effect: Callable[[], Any] | None = None,
    ):
        self._operation_processor_getter = operation_processor_getter
        self._post_trigger_side_effect = post_trigger_side_effect
        self._operation_processor: OperationProcessor = None  # type: ignore[assignment]

    @noop_if_evaluated
    def evaluate(self) -> None:
        self._operation_processor = self._operation_processor_getter()
        self._operation_processor.start()

    @property
    def is_evaluated(self) -> bool:
        return self._operation_processor is not None

    @trigger_evaluation
    def enqueue_operation(self, op: Operation, *, wait: bool) -> None:
        self._operation_processor.enqueue_operation(op, wait=wait)

    @property
    @trigger_evaluation
    def operation_storage(self) -> OperationStorage:
        return self._operation_processor.operation_storage

    @property
    @trigger_evaluation
    def data_path(self) -> Path:
        if isinstance(self._operation_processor, Resource):
            return self._operation_processor.data_path
        raise NotImplementedError

    @trigger_evaluation
    def start(self) -> None:
        self._operation_processor.start()

    @noop_if_not_evaluated
    def pause(self) -> None:
        self._operation_processor.pause()

    @noop_if_not_evaluated
    def resume(self) -> None:
        self._operation_processor.resume()

    @noop_if_not_evaluated
    def flush(self) -> None:
        self._operation_processor.flush()

    @noop_if_not_evaluated
    def wait(self) -> None:
        self._operation_processor.wait()

    @noop_if_not_evaluated
    def stop(self, seconds: float | None = None) -> None:
        self._operation_processor.stop(seconds=seconds)

    @noop_if_not_evaluated
    def close(self) -> None:
        self._operation_processor.close()
