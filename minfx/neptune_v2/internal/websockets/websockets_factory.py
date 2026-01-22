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

__all__ = ["WebsocketsFactory"]

import threading
from typing import TYPE_CHECKING

from minfx.neptune_v2.common.websockets.reconnecting_websocket import ReconnectingWebsocket

if TYPE_CHECKING:
    from requests_oauthlib import OAuth2Session


class WebsocketsFactory:
    def __init__(self, url: str, session: OAuth2Session, proxies: dict | None = None):
        self._url = url
        self._session = session
        self._proxies = proxies

    def create(self) -> None:
        return ReconnectingWebsocket(
            url=self._url,
            oauth2_session=self._session,
            shutdown_event=threading.Event(),
            proxies=self._proxies,
        )
