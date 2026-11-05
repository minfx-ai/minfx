# backends

Backend implementations for communicating with Neptune services.

## Purpose

The internal backends module implements the communication layer between the
Neptune client and various Neptune backend services.
[`NeptuneBackend`] defines the abstract base class for all backend
implementations.
[`HostedNeptuneBackend`], [`OfflineNeptuneBackend`], and
[`NeptuneBackendMock`] provide hosted, offline, and test implementations.
[`MultiBackend`] fans out operations to multiple backends in parallel.
[`factory.py`] selects and constructs backend instances from credentials and
mode.
[`operation_api_object_converter.py`] encodes IEEE 754 special float values
as strings such as [`NaN`], [`PosInf`], and [`NegInf`] for JSON serialization.

## Subdirectories / Files

- `./__init__.py` - Package marker with no public re-exports.
- `./api_model.py` - API data models for projects, attributes, and experiments.
- `./backend_config.py` - [`BackendConfig`] and multi-backend token parsing.
- `./factory.py` - [`get_backend`] factory for creating backend instances.
- `./hosted_artifact_operations.py` - Artifact track and list hosted
  operations.
- `./hosted_client.py` - HTTP and Swagger client creation for hosted services.
- `./hosted_file_operations.py` - File and file-set upload and download for
  hosted backends.
- `./hosted_neptune_backend.py` - [`HostedNeptuneBackend`] for Neptune hosted
  service API communication.
- `./multi_backend.py` - [`MultiBackend`] composite backend with health
  tracking.
- `./neptune_backend.py` - [`NeptuneBackend`] abstract base class.
- `./neptune_backend_mock.py` - [`NeptuneBackendMock`] in-memory mock backend
  for testing.
- `./offline_neptune_backend.py` - [`OfflineNeptuneBackend`] for offline mode
  without network access.
- `./operation_api_name_visitor.py` - Maps operations to API field names.
- `./operation_api_object_converter.py` - Converts operations to JSON-
  serializable dicts.
- `./operations_preprocessor.py` - [`OperationsPreprocessor`] batches and
  deduplicates operations before transmission.
- `./project_name_lookup.py` - [`project_name_lookup`] resolves project names
  from environment variables.
- `./swagger_client_wrapper.py` - [`SwaggerClientWrapper`] wraps OpenAPI
  Swagger clients with error handling.
- `./utils.py` - Batch execution, caching, and response adapter utilities.

## Usages

- [`factory.py`] creates the appropriate backend from credentials and
  [`Mode`].
- Hosted backends use [`hosted_client.py`] to call Neptune APIs and
  [`hosted_file_operations.py`] for uploads.
- [`OperationsPreprocessor`] prepares operation batches before
  [`HostedNeptuneBackend`] sends them to the server.
- [`operation_api_object_converter.py`] serializes operations including
  special floats like [`float("nan")`] and [`float("inf")`].
- Users interact with backends indirectly through the high-level Neptune API.
- See [`../README.md`] for the parent internal module overview.


[`NeptuneBackend`]: neptune_backend.NeptuneBackend
[`HostedNeptuneBackend`]: hosted_neptune_backend.HostedNeptuneBackend
[`OfflineNeptuneBackend`]: offline_neptune_backend.OfflineNeptuneBackend
[`NeptuneBackendMock`]: neptune_backend_mock.NeptuneBackendMock
[`MultiBackend`]: multi_backend.MultiBackend
[`BackendConfig`]: backend_config.BackendConfig
[`get_backend`]: factory.get_backend
[`OperationsPreprocessor`]: operations_preprocessor.OperationsPreprocessor
[`project_name_lookup`]: project_name_lookup.project_name_lookup
[`SwaggerClientWrapper`]: swagger_client_wrapper.SwaggerClientWrapper
[`Mode`]: ../../types/mode.Mode
[`NaN`]: operation_api_object_converter.py
[`PosInf`]: operation_api_object_converter.py
[`NegInf`]: operation_api_object_converter.py
[`float("nan")`]: operation_api_object_converter.py
[`float("inf")`]: operation_api_object_converter.py
[`factory.py`]: factory.py
[`hosted_client.py`]: hosted_client.py
[`hosted_file_operations.py`]: hosted_file_operations.py
[`operation_api_object_converter.py`]: operation_api_object_converter.py
[`../README.md`]: ../README.md

---
2026-11-05T16:01:08
