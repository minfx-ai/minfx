# websockets

Internal WebSocket coordination for real-time Neptune client features.

## Purpose

The internal websockets module coordinates WebSocket connections for real-time
communication features like live monitoring and signals.
[`ws::Factory`] builds authenticated [`ws::Reconnecting`] instances.
[`signals::Job`] listens for remote stop and abort signals.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./websocket_signals_background_job.py` - [`signals::Job`] background listener
  for stop and abort signals.
- `./websockets_factory.py` - [`ws::Factory`] for creating
  [`ws::Reconnecting`] connections.

## Usages

- The Neptune client uses this module internally to establish and manage
  WebSocket connections for real-time features.
- [`ws::Factory`] creates [`ws::Reconnecting`] instances with OAuth2 session
  credentials and optional proxy settings.
- [`signals::Job`] runs a daemon thread that parses incoming signal messages
  and stops or aborts the active run.


[`ws::Factory`]: websockets_factory.WebsocketsFactory
[`signals::Job`]: websocket_signals_background_job.WebsocketSignalsBackgroundJob
[`ws::Reconnecting`]: ../../common/websockets/reconnecting_websocket.py

---
2026-08-07T13:46:32
