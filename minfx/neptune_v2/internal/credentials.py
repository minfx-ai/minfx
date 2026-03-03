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
from __future__ import annotations

__all__ = ["Credentials"]

import base64
from dataclasses import dataclass
import json
import os

from minfx.neptune_v2.common.envs import API_TOKEN_ENV_NAME
from minfx.neptune_v2.common.exceptions import NeptuneInvalidApiTokenException
from minfx.neptune_v2.constants import ANONYMOUS_API_TOKEN
from minfx.neptune_v2.exceptions import NeptuneMissingApiTokenException
from minfx.neptune_v2.internal.constants import ANONYMOUS_API_TOKEN_CONTENT


@dataclass(frozen=True)
class Credentials:
    api_token: str
    api_address: str

    @classmethod
    def from_token(cls, api_token: str | None = None) -> Credentials:
        if api_token is None:
            api_token = os.getenv(API_TOKEN_ENV_NAME)

        if api_token == ANONYMOUS_API_TOKEN:
            api_token = ANONYMOUS_API_TOKEN_CONTENT

        if api_token is None:
            raise NeptuneMissingApiTokenException

        api_token = api_token.strip()
        token_dict = Credentials._api_token_to_dict(api_token)
        if "api_address" not in token_dict:
            raise NeptuneInvalidApiTokenException
        api_address = token_dict["api_address"]

        return Credentials(
            api_token=api_token,
            api_address=api_address,
        )

    @staticmethod
    def _api_token_to_dict(api_token: str) -> dict[str, str]:
        try:
            return json.loads(base64.b64decode(api_token.encode()).decode("utf-8"))
        except Exception:
            raise NeptuneInvalidApiTokenException
