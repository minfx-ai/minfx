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
__all__ = ["ContainerState", "ForkingState", "OperationAcceptance"]

from enum import Enum


class ContainerState(Enum):
    CREATED = "created"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ForkingState(Enum):
    """Represents whether the container is currently in a forking process."""

    IDLE = "idle"
    FORKING = "forking"

    def is_forking(self) -> bool:
        """Returns True if the container is currently being forked."""
        return self == ForkingState.FORKING


class OperationAcceptance(Enum):
    """Represents whether the processor is accepting new operations."""

    ACCEPTING = "accepting"
    REJECTING = "rejecting"

    def is_accepting(self) -> bool:
        """Returns True if the processor is accepting operations."""
        return self == OperationAcceptance.ACCEPTING
