# aws

Integration with Amazon Web Services for Neptune experiment tracking.

## Purpose

This module provides integration with Amazon Web Services (AWS).
The AWS integration enables Neptune to work seamlessly with AWS services.
It supports artifact storage and cloud-based experiment tracking.
This integration requires the [`neptune-aws`] package for S3 artifact
storage, AWS-specific utilities, and cloud resource tracking.

## Subdirectories / Files

- `./__init__.py` - Package entry that loads [`neptune-aws`] when installed.

## Usages

- Install [`neptune-aws`] with pip before importing this module.
- The integration is automatically available when [`neptune-aws`] is
  installed.
- Import AWS-specific functionality through this module.
- See [`../README.md`] for information about Neptune integrations.


[`neptune-aws`]: https://pypi.org/project/neptune-aws/
[`../README.md`]: ../README.md

---
2026-08-07T13:46:32
