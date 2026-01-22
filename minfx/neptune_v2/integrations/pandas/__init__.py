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

__all__ = ["to_pandas"]

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    TypeAlias,
)

import pandas as pd

from minfx.neptune_v2.internal.backends.api_model import (
    AttributeType,
    AttributeWithProperties,
    LeaderboardEntry,
)
from minfx.neptune_v2.internal.utils.logger import get_logger
from minfx.neptune_v2.internal.utils.run_state import RunState

if TYPE_CHECKING:
    from minfx.neptune_v2.table import Table

logger = get_logger()

# Type alias for attribute values in pandas DataFrame
PandasAttributeValue: TypeAlias = str | float | int | bool | datetime | None


def to_pandas(table: Table) -> pd.DataFrame:
    def make_attribute_value(attribute: AttributeWithProperties) -> PandasAttributeValue:
        _type = attribute.type
        _properties = attribute.properties
        if _type == AttributeType.RUN_STATE:
            return RunState.from_api(_properties.get("value")).value
        if _type in (
            AttributeType.FLOAT,
            AttributeType.INT,
            AttributeType.BOOL,
            AttributeType.STRING,
            AttributeType.DATETIME,
        ):
            return _properties.get("value")
        if _type == AttributeType.FLOAT_SERIES:
            return _properties.get("last")
        if _type == AttributeType.STRING_SERIES:
            return _properties.get("last")
        if _type == AttributeType.IMAGE_SERIES:
            return None
        if _type in (AttributeType.FILE, AttributeType.FILE_SET):
            return None
        if _type == AttributeType.STRING_SET:
            values = _properties.get("values")
            return ",".join(values) if values else ""
        if _type == AttributeType.GIT_REF:
            commit = _properties.get("commit")
            return commit.get("commitId") if commit else None
        if _type == AttributeType.NOTEBOOK_REF:
            return _properties.get("notebookName")
        if _type == AttributeType.ARTIFACT:
            return _properties.get("hash")
        logger.error(
            "Attribute type %s not supported in this version, yielding None. Recommended client upgrade.",
            _type,
        )
        return None

    def make_row(entry: LeaderboardEntry) -> dict[str, PandasAttributeValue]:
        row: dict[str, PandasAttributeValue] = {}
        for attr in entry.attributes:
            value = make_attribute_value(attr)
            if value is not None:
                row[attr.path] = value
        return row

    def sort_key(attr: str) -> tuple[int, str]:
        domain = attr.split("/")[0]
        if domain == "sys":
            return 0, attr
        if domain == "monitoring":
            return 2, attr
        return 1, attr

    rows = {n: make_row(entry) for (n, entry) in enumerate(table._entries)}

    df = pd.DataFrame.from_dict(data=rows, orient="index")
    df = df.reindex(sorted(df.columns, key=sort_key), axis="columns")

    return df
