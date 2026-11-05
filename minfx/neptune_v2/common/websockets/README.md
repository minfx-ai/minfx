# websockets

WebSocket communication with automatic reconnection for Neptune services.

## Purpose

This module implements reliable WebSocket connections with automatic
reconnection and error handling for real-time communication with Neptune
services.
[`ReconnectingWebsocket`] wraps [`WebsocketClientAdapter`] and retries
connections with exponential backoff.
It handles OAuth2 authentication, proxy configuration, and graceful
shutdown.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./reconnecting_websocket.py` - [`ReconnectingWebsocket`] with reconnection
  logic.
- `./websocket_client_adapter.py` - [`WebsocketClientAdapter`] WebSocket
  wrapper.

## Usages

- [`WebsocketsFactory`] creates [`ReconnectingWebsocket`] instances for the
  internal WebSocket layer.
- [`signals::Job`] listens for abort and stop signals via
  [`ReconnectingWebsocket`].
- See [`../README.md`] for the parent common utilities overview.


[`ReconnectingWebsocket`]: reconnecting_websocket.ReconnectingWebsocket
[`WebsocketClientAdapter`]: websocket_client_adapter.WebsocketClientAdapter
[`WebsocketsFactory`]: ../../internal/websockets/websockets_factory.py
[`signals::Job`]: ../../internal/websockets/websocket_signals_background_job.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
