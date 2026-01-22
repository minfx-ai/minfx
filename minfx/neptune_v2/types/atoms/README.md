# Atom Value Types

This module provides value type classes for atomic attributes.

## Purpose

The atom value types module defines the data classes representing different types of atomic values that can be stored in Neptune attributes.

## Key Components

- `Atom`: Base class for all atomic value types
- `Boolean`: Boolean value type
- `Integer`: Integer value type
- `Float`: Floating-point value type
- `String`: String value type
- `Datetime`: Datetime value type
- `File`: File value type
- `Artifact`: Artifact reference value type
- `GitRef`: Git reference value type

## Functionality

These value types:
- Represent different data types for atomic values
- Provide type-safe value containers
- Support serialization and deserialization
- Enable type checking and validation

## Usage

These types are used internally to represent values stored in atomic attributes. Users typically don't interact with these classes directly but use them implicitly through attribute assignments.

## Parent Module

See `../README.md` for information about Neptune types.

---
7dcfce5a 2026-01-18T14:43:38
