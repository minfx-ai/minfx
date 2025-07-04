# Minfx

A minimal Python package for the minfx project.

## Installation

```bash
pip install minfx
```

## Development Installation

```bash
git clone https://github.com/minfx-ai/minfx.git
pip install -e .
```

For development with all dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
import minfx
print(f"Minfx version: {minfx.__version__}")
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
```

## Building for Distribution

```bash
python -m build
```
