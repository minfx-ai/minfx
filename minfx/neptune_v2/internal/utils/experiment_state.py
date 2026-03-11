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
__all__ = ["ExperimentState"]

import enum

from minfx.neptune_v2.common.exceptions import NeptuneException


# API mapping dictionaries (module-level to avoid Enum member conflicts)
_API_TO_STATE: dict[str, "ExperimentState"] = {}
_STATE_TO_API: dict["ExperimentState", str] = {}


class ExperimentState(enum.Enum):
    """Represents the state of a Neptune experiment/run."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"

    @classmethod
    def from_string(cls, value: str) -> "ExperimentState":
        """Create ExperimentState from a string value (case-insensitive)."""
        try:
            return cls(value.capitalize())
        except ValueError as e:
            raise NeptuneException(f"Can't map ExperimentState from string: {value}") from e

    @classmethod
    def from_api(cls, value: str) -> "ExperimentState":
        """Create ExperimentState from an API response value."""
        if value not in _API_TO_STATE:
            raise NeptuneException(f"Unknown ExperimentState from API: {value}")
        return _API_TO_STATE[value]

    def to_api(self) -> str:
        """Convert ExperimentState to API format."""
        return _STATE_TO_API[self]


# Initialize the API mappings after the class is fully defined
# This cleanly separates the enum values from API serialization concerns
_API_TO_STATE.update(
    {
        "running": ExperimentState.ACTIVE,
        "idle": ExperimentState.INACTIVE,
    }
)
_STATE_TO_API.update(
    {
        ExperimentState.ACTIVE: "running",
        ExperimentState.INACTIVE: "idle",
    }
)
