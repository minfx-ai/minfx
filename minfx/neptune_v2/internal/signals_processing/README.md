# Internal Signals Processing

This module provides signal handling for graceful shutdown and cleanup.

## Purpose

The signals processing module handles OS signals (SIGTERM, SIGINT, etc.) to ensure graceful shutdown of Neptune runs when processes are interrupted.

## Key Components

- `signals.py`: Signal definitions and handlers
- `signals_processor.py`: Signal processing logic
- `background_job.py`: Background job for signal monitoring
- `utils.py`: Signal processing utilities

## Functionality

This module provides:
- OS signal registration and handling
- Graceful shutdown on process termination
- Cleanup coordination across components
- Background signal monitoring

## Usage

This module is used internally by the Neptune client to automatically handle process interruptions and ensure data is properly flushed and connections are closed before exit.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
7dcfce5a 2026-01-18T14:43:38
