# minfx

## Purpose

Neptune [announced the shutdown of its
services](https://docs.neptune.ai/transition_hub/).

[Minfx](https://minfx.ai) is your solution.

We're the fastest experiment tracker on the market, built specifically as a
drop-in replacement for Neptune.
We offer:

- **One-line code change** - same APIs, instant compatibility
- **Automatic data migration** - we'll transfer your data for you
- **High-performance UI** - >60 FPS rendering for smooth interactions
- **Multi-backend support** - extra reliability and redundancy

## Subdirectories / Files

- `./minfx/` - Python package source with Neptune v2 and v3 drop-in clients.
- `./scripts/` - Build, format, check, and packaging helper shell scripts.
- `./LICENSE` - MIT license text for the minfx distribution.
- `./Makefile` - Development targets for install, test, build, and release.
- `./MANIFEST.in` - Source distribution manifest for setuptools packaging.
- `./pyproject.toml` - Project metadata, dependencies, and tool configuration.
- `./setup.py` - Setuptools entry point for legacy packaging workflows.
- `./uv.lock` - Locked dependency versions for reproducible uv installs.
- `./VERSION` - Package version file used by setuptools dynamic versioning.

## Usages

- Drop-in replacement for Neptune: use [`import minfx as neptune`] instead of
  [`import neptune`].
- Visit https://minfx.ai for product details, migration help, and onboarding.
- Run make install_dev from this directory to install the package in editable
  mode with dev dependencies.
- Run make test to execute unit tests against bundled Neptune v2 code.


[`import minfx as neptune`]: minfx/__init__.py
[`import neptune`]: minfx/neptune_v2/__init__.py

---
2026-08-07T13:46:32
