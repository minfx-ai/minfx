# WebSockets

This module provides WebSocket communication functionality with automatic reconnection.

## Purpose

The websockets module implements reliable WebSocket connections with automatic reconnection and error handling for real-time communication with Neptune services.

## Key Components

- `ReconnectingWebsocket`: WebSocket client with automatic reconnection logic
- `WebsocketClientAdapter`: Adapter for the underlying WebSocket client library

## Functionality

This module provides:
- Automatic reconnection with exponential backoff
- Error handling for connection failures
- OAuth2 authentication support
- Graceful shutdown handling
- Proxy support

## Usage

This module is used internally by the Neptune client for real-time communication features, ensuring reliable connections even in unstable network conditions.

## Parent Module

See `../README.md` for information about the common utilities system.

---
7dcfce5a 2026-01-18T14:43:38
