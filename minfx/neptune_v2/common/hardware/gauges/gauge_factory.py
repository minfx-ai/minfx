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
from minfx.neptune_v2.common.hardware.gauges.cpu import (
    CGroupCpuUsageGauge,
    SystemCpuUsageGauge,
)
from minfx.neptune_v2.common.hardware.gauges.gauge import Gauge
from minfx.neptune_v2.common.hardware.gauges.gauge_mode import GaugeMode
from minfx.neptune_v2.common.hardware.gauges.gpu import (
    GpuMemoryGauge,
    GpuPowerGauge,
    GpuUsageGauge,
)
from minfx.neptune_v2.common.hardware.gauges.memory import (
    CGroupMemoryUsageGauge,
    SystemMemoryUsageGauge,
)


class GaugeFactory:
    def __init__(self, gauge_mode: str) -> None:
        self.__gauge_mode = gauge_mode

    def create_cpu_usage_gauge(self) -> Gauge:
        if self.__gauge_mode == GaugeMode.SYSTEM:
            return SystemCpuUsageGauge()
        if self.__gauge_mode == GaugeMode.CGROUP:
            return CGroupCpuUsageGauge()
        raise self.__invalid_gauge_mode_exception

    def create_memory_usage_gauge(self) -> Gauge:
        if self.__gauge_mode == GaugeMode.SYSTEM:
            return SystemMemoryUsageGauge()
        if self.__gauge_mode == GaugeMode.CGROUP:
            return CGroupMemoryUsageGauge()
        raise self.__invalid_gauge_mode_exception

    @staticmethod
    def create_gpu_usage_gauge(card_index: int) -> GpuUsageGauge:
        return GpuUsageGauge(card_index=card_index)

    @staticmethod
    def create_gpu_memory_gauge(card_index: int) -> GpuMemoryGauge:
        return GpuMemoryGauge(card_index=card_index)

    @staticmethod
    def create_gpu_power_gauge(card_index: int) -> GpuPowerGauge:
        return GpuPowerGauge(card_index=card_index)

    def __invalid_gauge_mode_exception(self) -> ValueError:
        return ValueError(f"Invalid gauge mode: {self.__gauge_mode}")
