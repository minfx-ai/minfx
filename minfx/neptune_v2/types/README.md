# Types

This module provides type definitions for Neptune values and attributes.

## Purpose

The types module defines the value types and type system used throughout Neptune for representing different kinds of data.

## Key Components

- `value.py`: Base value class
- `value_visitor.py`: Value visitor pattern implementation
- `value_copy.py`: Value copying utilities
- `type_casting.py`: Type casting and conversion
- `namespace.py`: Namespace type
- `file_set.py`: File set type
- `mode.py`: Neptune mode enumeration
- `model_version_stage.py`: Model version stage enumeration

## Submodules

- `atoms/`: Atomic value types
- `series/`: Series value types
- `sets/`: Set value types

## Functionality

This module provides:
- Type definitions for all Neptune values
- Type casting and conversion
- Value visitor pattern for type-safe operations
- Namespace and file set types
- Mode and stage enumerations

## Usage

These types are used internally to represent values throughout Neptune. Users typically interact with them indirectly through attribute operations.

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
7dcfce5a 2026-01-18T14:43:38
