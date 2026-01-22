# API

This module provides the public API for fetching and querying Neptune data.

## Purpose

The API module implements the client-side API for fetching experiment data, searching runs, and querying Neptune objects.

## Key Components

- `dtos.py`: Data transfer objects for API responses (FileEntry, etc.)
- `searching_entries.py`: Entry searching and filtering functionality
- `requests_utils.py`: HTTP request utilities for API calls

## Functionality

This module provides:
- Fetching run and project data
- Searching and filtering experiments
- Downloading files and artifacts
- Querying metadata and metrics
- Leaderboard access

## Usage

This module is used through high-level Neptune objects like `Run` and `Project` to fetch data from Neptune services.

## Parent Module

See `../README.md` for information about the Neptune v2 client.

---
7dcfce5a 2026-01-18T14:43:38
