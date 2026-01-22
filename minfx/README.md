# minfx Package

This is the source directory for the `minfx` Python package.

## Package Structure

```
minfx/
├── __init__.py           # Package initialization with version info
├── neptune_v2/           # Neptune v2 (legacy) drop-in replacement
└── neptune_v3.py         # Neptune v3 (scale) drop-in replacement
```

## Modules

### neptune_v2

Drop-in replacement for the legacy Neptune client (`neptune` package). Contains:

- **api/**: API utilities and DTOs for server communication
- **attributes/**: Attribute types (String, Float, FileSeries, etc.)
- **cli/**: Command-line interface (`minfx status`, `minfx sync`, etc.)
- **common/**: Shared utilities and warnings
- **core/**: Core components (operation storage, disk queue)
- **integrations/**: ML framework integrations (PyTorch, TensorFlow, XGBoost, etc.)
- **internal/**: Internal implementation (backends, operations, signals)
- **metadata_containers/**: Run, Project, Model containers
- **types/**: Type definitions (atoms, series, sets)

Usage:
```python
import minfx.neptune_v2 as neptune

run = neptune.init_run(project="workspace/project")
run["metrics/accuracy"] = 0.95
run.stop()
```

### neptune_v3

Drop-in replacement for Neptune Scale (`neptune_scale` package).

Usage:
```python
import minfx.neptune_v3 as neptune_scale

run = neptune_scale.Run(project="workspace/project")
run.log_metrics({"accuracy": 0.95})
run.close()
```

## Development

See the parent [README.md](../README.md) for installation and development instructions.
