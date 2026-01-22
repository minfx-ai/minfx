# Internal Notebooks

This module provides Jupyter notebook integration functionality.

## Purpose

The internal notebooks module handles detection and integration with Jupyter notebooks, including cell tracking and notebook metadata extraction.

## Key Components

- `notebooks.py`: Notebook detection and metadata extraction
- `comm.py`: Communication with Jupyter kernel for notebook tracking

## Functionality

This module provides:
- Jupyter notebook environment detection
- Notebook ID and path extraction
- Cell execution tracking
- IPython kernel communication
- Notebook checkpoint creation

## Usage

This module is used internally by the Neptune client to automatically detect when running in Jupyter notebooks and track notebook-specific metadata.

## Parent Module

See `../README.md` for information about internal Neptune components.

---
7dcfce5a 2026-01-18T14:43:38
