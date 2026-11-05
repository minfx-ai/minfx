# patches

Patches and workarounds for third-party library issues in Neptune.

## Purpose

The patches module contains modifications to third-party library behavior.
These changes fix bugs or adapt functionality for Neptune's specific needs.
[`patches::apply_patches`] registers patch callables and applies them before
patched libraries are used.
The [`bravado::patch`] callable replaces bravado-core post-processing so
OpenAPI specs resolve without json-schema.org requests.

## Subdirectories / Files

- `./__init__.py` - Exports [`patches::apply_patches`] and the patch
  registry.
- `./bravado.py` - Bravado OpenAPI client workaround for offline use.

## Usages

- The Neptune client imports [`patches::apply_patches`] from
  [`neptune_v2::__init__`] and runs it during package initialization.
- Call [`patches::apply_patches`] before using patched third-party objects if
  you import Neptune modules directly.
- See [`../README.md`] for the parent common utilities overview.


[`patches::apply_patches`]: __init__.py
[`bravado::patch`]: bravado.py
[`neptune_v2::__init__`]: ../../__init__.py
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
