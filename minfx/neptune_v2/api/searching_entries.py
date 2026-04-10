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

__all__ = ["get_single_page", "iter_over_pages"]

from typing import (
    TYPE_CHECKING,
    Generator,
    Iterable,
)

from bravado.client import construct_request  # type: ignore[import-untyped]
from bravado.config import RequestConfig  # type: ignore[import-untyped]

from typing_extensions import (
    Literal,
    TypeAlias,
)

from minfx.neptune_v2.internal.backends.api_model import (
    AttributeType,
    AttributeWithProperties,
    LeaderboardEntry,
)
from minfx.neptune_v2.internal.backends.hosted_client import DEFAULT_REQUEST_KWARGS
from minfx.neptune_v2.internal.backends.utils import construct_progress_bar
from minfx.neptune_v2.internal.init.parameters import MAX_SERVER_OFFSET

if TYPE_CHECKING:
    from minfx.neptune_v2.internal.backends.swagger_client_wrapper import SwaggerClientWrapper
    from minfx.neptune_v2.internal.id_formats import UniqueId
    from minfx.neptune_v2.typing import ProgressBarType


SUPPORTED_ATTRIBUTE_TYPES = {item.value for item in AttributeType}

SORT_BY_COLUMN_TYPE: TypeAlias = Literal["string", "datetime", "integer", "boolean", "float"]


class NoLimit(int):
    def __gt__(self, other: float) -> bool:
        return True

    def __lt__(self, other: float) -> bool:
        return False

    def __ge__(self, other: float) -> bool:
        return True

    def __le__(self, other: float) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return False

    def __hash__(self) -> int:
        return hash(id(self))

    def __ne__(self, other: object) -> bool:
        return True


def get_single_page(
    *,
    client: SwaggerClientWrapper,
    project_id: UniqueId,
    attributes_filter: dict[str, object],
    limit: int,
    offset: int,
    sort_by: str,
    sort_by_column_type: SORT_BY_COLUMN_TYPE,
    ascending: bool,
    types: Iterable[str] | None,
    searching_after: str | None,
    tags: list[str] | None = None,
    run_ids: list[str] | None = None,
    owners: list[str] | None = None,
    states: list[str] | None = None,
    trashed: bool | None = False,
) -> dict[str, object]:
    sort_by_column_type = sort_by_column_type if sort_by_column_type else AttributeType.STRING.value

    sorting = (
        {
            "sorting": {
                "dir": "ascending" if ascending else "descending",
                "aggregationMode": "none",
                "sortBy": {
                    "name": sort_by,
                    "type": sort_by_column_type if sort_by_column_type else AttributeType.STRING.value,
                },
            }
        }
        if sort_by
        else {}
    )

    attribute_strings = [
        item.get("path")
        for item in attributes_filter.get("attributeFilters", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    ]
    mapped_states: list[str] | None = None
    if states:
        mapped_states = []
        for state in states:
            normalized = state.lower()
            if normalized == "active":
                mapped_states.append("running")
            elif normalized == "inactive":
                mapped_states.extend(["idle", "crashed"])
            else:
                mapped_states.append(normalized)

    params = {
        "projectIdentifier": project_id,
        "type": types,
        "params": {
            **sorting,
            **attributes_filter,
            "pagination": {"limit": limit, "offset": offset},
            **({"tags": tags} if tags else {}),
            **({"runIds": run_ids} if run_ids else {}),
            **({"owners": owners} if owners else {}),
            **({"experimentStates": mapped_states} if mapped_states else {}),
            **({"trashed": trashed} if trashed is not None else {}),
            **({"attributeStrings": attribute_strings} if attribute_strings else {}),
        },
    }

    request_options = DEFAULT_REQUEST_KWARGS.get("_request_options", {})
    request_config = RequestConfig(request_options, True)
    request_params = construct_request(client.api.searchLeaderboardEntries, request_options, **params)

    http_client = client.swagger_spec.http_client

    return (
        http_client.request(request_params, operation=None, request_config=request_config)
        .response()
        .incoming_response.json()
    )


def to_leaderboard_entry(entry: dict[str, object]) -> LeaderboardEntry:
    experiment_id = entry["experimentId"]
    attributes_raw = entry["attributes"]
    if not isinstance(experiment_id, str):
        raise TypeError(f"Expected experimentId to be str, got {type(experiment_id)}")
    # Handle both list format (legacy) and dict format (new: keyed by AttributeId)
    if isinstance(attributes_raw, dict):
        attributes_raw = list(attributes_raw.values())
    if not isinstance(attributes_raw, list):
        raise TypeError(f"Expected attributes to be list or dict, got {type(attributes_raw)}")
    return LeaderboardEntry(
        id=experiment_id,
        attributes=[
            AttributeWithProperties(
                path=attr["name"],  # type: ignore[index]
                type=AttributeType(attr["type"]),  # type: ignore[index]
                properties=attr[f"{attr['type']}Properties"],  # type: ignore[index]
            )
            for attr in attributes_raw
            if isinstance(attr, dict) and attr.get("type") in SUPPORTED_ATTRIBUTE_TYPES
        ],
    )


def find_attribute(*, entry: LeaderboardEntry, path: str) -> AttributeWithProperties | None:
    return next((attr for attr in entry.attributes if attr.path == path), None)


def iter_over_pages(
    *,
    step_size: int,
    limit: int | None,
    offset: int = 0,
    sort_by: str,
    sort_by_column_type: SORT_BY_COLUMN_TYPE,
    ascending: bool,
    progress_bar: ProgressBarType | None,
    max_offset: int = MAX_SERVER_OFFSET,
    **kwargs: object,
) -> Generator[LeaderboardEntry, None, None]:
    searching_after = None
    last_page = None

    total = get_single_page(
        limit=0,
        offset=offset,
        sort_by=sort_by,
        ascending=ascending,
        sort_by_column_type=sort_by_column_type,
        searching_after=None,
        **kwargs,
    ).get("matchingItemCount", 0)

    limit = limit if limit is not None else NoLimit()

    total = min(limit, total)

    progress_bar = False if total <= step_size else progress_bar  # disable progress bar if only one page is fetched

    extracted_records = 0

    with construct_progress_bar(progress_bar, "Fetching table...") as bar:
        # beginning of the first page
        bar.update(
            by=0,
            total=total,
        )

        while True:
            if last_page:
                page_attribute = find_attribute(entry=last_page[-1], path=sort_by)

                if not page_attribute:
                    raise ValueError(f"Cannot find attribute {sort_by} in last page")

                searching_after = page_attribute.properties["value"]

            page_start_offset = offset if last_page is None else 0
            if page_start_offset >= max_offset:
                return

            for local_offset in range(page_start_offset, max_offset, step_size):
                local_limit = min(step_size, max_offset - local_offset)
                if extracted_records + local_limit > limit:
                    local_limit = limit - extracted_records
                result = get_single_page(
                    limit=local_limit,
                    offset=local_offset,
                    sort_by=sort_by,
                    sort_by_column_type=sort_by_column_type,
                    searching_after=searching_after,
                    ascending=ascending,
                    **kwargs,
                )

                # fetch the item count everytime a new page is started (except for the very fist page)
                if local_offset == page_start_offset and last_page is not None:
                    total += result.get("matchingItemCount", 0)

                total = min(total, limit)

                page = _entries_from_page(result)
                extracted_records += len(page)
                bar.update(by=len(page), total=total)

                if not page:
                    return

                yield from page

                if extracted_records == limit:
                    return

                last_page = page


def _entries_from_page(single_page: dict[str, object]) -> list[LeaderboardEntry]:
    entries = single_page.get("entries", [])
    if not isinstance(entries, list):
        return []
    return list(map(to_leaderboard_entry, entries))
