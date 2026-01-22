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

if TYPE_CHECKING:
    from minfx.neptune_v2.common.hardware.gauges.gauge import Gauge


class Metric:
    def __init__(
        self,
        name: str,
        description: str,
        resource_type: str,
        unit: str,
        min_value: float,
        max_value: float,
        gauges: list[Gauge],
        internal_id: str | None = None,
    ) -> None:
        self.__internal_id = internal_id
        self.__name = name
        self.__description = description
        self.__resource_type = resource_type
        self.__unit = unit
        self.__min_value = min_value
        self.__max_value = max_value
        self.__gauges = gauges

    @property
    def internal_id(self) -> str | None:
        return self.__internal_id

    @internal_id.setter
    def internal_id(self, value: str | None) -> None:
        self.__internal_id = value

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def resource_type(self) -> str:
        return self.__resource_type

    @property
    def unit(self) -> str:
        return self.__unit

    @property
    def min_value(self) -> float:
        return self.__min_value

    @property
    def max_value(self) -> float:
        return self.__max_value

    @property
    def gauges(self) -> list[Gauge]:
        return self.__gauges

    def __repr__(self) -> str:
        return (
            f"Metric(internal_id={self.internal_id}, name={self.name}, description={self.description}, resource_type={self.resource_type}, unit={self.unit}, min_value={self.min_value}, "
            f"max_value={self.max_value}, gauges={self.gauges})"
        )

    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and repr(self) == repr(other)

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__.__name__,
                self.__internal_id,
                self.__name,
                self.__description,
                self.__resource_type,
                self.__unit,
                self.__min_value,
                self.__max_value,
                tuple(self.__gauges) if self.__gauges else None,
            )
        )


class MetricResourceType:
    CPU = "CPU"
    RAM = "MEMORY"
    GPU = "GPU"
    GPU_RAM = "GPU_MEMORY"
    GPU_POWER = "GPU_POWER"
    OTHER = "OTHER"
