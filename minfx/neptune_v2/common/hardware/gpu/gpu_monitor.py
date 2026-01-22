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

from typing import (
    Callable,
    TypeVar,
)

from minfx.neptune_v2.common.hardware.constants import MILLIWATTS_IN_ONE_WATT
from minfx.neptune_v2.common.warnings import (
    NeptuneWarning,
    warn_once,
)
from minfx.neptune_v2.vendor.pynvml import (
    NVMLError,
    nvmlDeviceGetCount,
    nvmlDeviceGetEnforcedPowerLimit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetPowerUsage,
    nvmlDeviceGetUtilizationRates,
    nvmlInit,
)

T = TypeVar("T")


class GPUMonitor:
    nvml_error_printed = False

    def get_card_count(self) -> int:
        return self.__nvml_get_or_else(nvmlDeviceGetCount, default=0)

    def get_card_usage_percent(self, card_index: int) -> float | None:
        return self.__nvml_get_or_else(
            lambda: float(nvmlDeviceGetUtilizationRates(nvmlDeviceGetHandleByIndex(card_index)).gpu)
        )

    def get_card_used_memory_in_bytes(self, card_index: int) -> int | None:
        return self.__nvml_get_or_else(lambda: nvmlDeviceGetMemoryInfo(nvmlDeviceGetHandleByIndex(card_index)).used)

    def get_card_power_usage(self, card_index: int) -> int | None:
        return self.__nvml_get_or_else(lambda: nvmlDeviceGetPowerUsage(nvmlDeviceGetHandleByIndex(card_index)))

    def get_card_max_power_rating(self) -> int:
        def read_max_power_rating() -> list[int] | int:
            return self.__nvml_get_or_else(
                lambda: [
                    nvmlDeviceGetEnforcedPowerLimit(nvmlDeviceGetHandleByIndex(card_index)) // MILLIWATTS_IN_ONE_WATT
                    for card_index in range(nvmlDeviceGetCount())
                ],
                default=0,
            )

        power_rating_per_card = read_max_power_rating()
        if isinstance(power_rating_per_card, int):
            return power_rating_per_card
        return max(power_rating_per_card) if power_rating_per_card else 0

    def get_top_card_memory_in_bytes(self) -> int:
        def read_top_card_memory_in_bytes() -> list[int] | int:
            return self.__nvml_get_or_else(
                lambda: [
                    nvmlDeviceGetMemoryInfo(nvmlDeviceGetHandleByIndex(card_index)).total
                    for card_index in range(nvmlDeviceGetCount())
                ],
                default=0,
            )

        memory_per_card = read_top_card_memory_in_bytes()
        if isinstance(memory_per_card, int):
            return memory_per_card
        return max(memory_per_card) if memory_per_card else 0

    def __nvml_get_or_else(self, getter: Callable[[], T], default: T | None = None) -> T | None:
        try:
            nvmlInit()
            return getter()
        except NVMLError as e:
            if not GPUMonitor.nvml_error_printed:
                warning = (
                    f"Info (NVML): {e}. GPU usage metrics may not be reported. For more information, "
                    "see https://docs-legacy.neptune.ai/help/nvml_error/"
                )
                warn_once(message=warning, exception=NeptuneWarning)
                GPUMonitor.nvml_error_printed = True
            return default
