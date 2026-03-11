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

__all__ = [
    "parse_dates",
]

from typing import (
    Generator,
    Iterable,
)

from minfx.neptune_v2.common.warnings import (
    NeptuneWarning,
    warn_once,
)
from minfx.neptune_v2.internal.backends.api_model import (
    AttributeType,
    AttributeWithProperties,
    LeaderboardEntry,
)
from minfx.neptune_v2.internal.utils.iso_dates import parse_iso_date


def parse_dates(leaderboard_entries: Iterable[LeaderboardEntry]) -> Generator[LeaderboardEntry, None, None]:
    yield from [_parse_entry(entry) for entry in leaderboard_entries]


def _parse_entry(entry: LeaderboardEntry) -> LeaderboardEntry:
    try:
        return LeaderboardEntry(
            entry.id,
            attributes=[
                (
                    AttributeWithProperties(
                        attribute.path,
                        attribute.type,
                        {
                            **attribute.properties,
                            "value": parse_iso_date(attribute.properties["value"]),
                        },
                    )
                    if attribute.type == AttributeType.DATETIME
                    else attribute
                )
                for attribute in entry.attributes
            ],
        )
    except ValueError:
        # the parsing format is incorrect
        warn_once(
            "Date parsing failed. The date format is incorrect. Returning as string instead of datetime.",
            exception=NeptuneWarning,
        )
        return entry
