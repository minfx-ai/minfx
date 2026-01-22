# Internal Backends

This module provides backend implementations for communicating with Neptune services.

## Purpose

The internal backends module implements the communication layer between the Neptune client and various Neptune backend services (hosted, offline, mock).

## Key Components

- `neptune_backend.py`: Abstract base class for all backend implementations
- `hosted_neptune_backend.py`: Backend for Neptune's hosted service
- `offline_neptune_backend.py`: Backend for offline mode (no network)
- `neptune_backend_mock.py`: Mock backend for testing
- `multi_backend.py`: Multiplexing backend for multiple backends
- `factory.py`: Factory for creating backend instances
- `api_model.py`: API data models
- `operations_preprocessor.py`: Operation preprocessing logic
- `swagger_client_wrapper.py`: Wrapper for OpenAPI/Swagger client

## Functionality

This module provides:
- Multiple backend implementations (hosted, offline, mock)
- API communication with Neptune services
- Operation serialization and transmission
- File and artifact upload/download
- Project and experiment management
- NQL (Neptune Query Language) support

## Usage

This module is used internally by the Neptune client to communicate with backend services. Users interact with backends indirectly through the high-level Neptune API.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
df913a83 2026-01-22T01:04:04
