.PHONY: install-build install-dev build-dev test test-neptune_v2 test-neptune_v2-e2e test-integrations test-multi-backend test-all build build-dist clean install-test install-prod version prepare deploy-pypi all all-release dev-setup quick-test check fmt

# Disable parallel execution - targets have strict ordering requirements
.NOTPARALLEL:

# Suppress hardlink warning when cache and target are on different filesystems
export UV_LINK_MODE=copy

# Install build tools and test dependencies
install-build:
	@echo "Installing build tools..."
	uv pip install build twine setuptools wheel pytest pytest-cov

# Install package in development mode
install-dev:
	@echo "Installing package in development mode..."
	uv pip install -e ".[dev]"

# Install package in development mode (respects MINATO_QUIET)
build-dev:
	@./scripts/build_dev.sh

# Run all unit tests in parallel on all cores, report durations to /tmp/tests.txt
test:
	@echo "Running all unit tests in parallel..."
	python -m pytest tests/test_minfx.py tests/neptune_v2/unit -n auto --durations=0 -q

# Run neptune_v2 e2e tests (requires live backend; excludes zenml which needs sklearn)
test-neptune_v2-e2e:
	@echo "Running neptune_v2 e2e tests..."
	python -m pytest tests/neptune_v2/e2e --ignore=tests/neptune_v2/e2e/integrations/test_zenml.py --durations=0 -v

# Run integration tests with heavy dependencies (matplotlib, pandas, plotly, etc.)
test-integrations:
	@echo "Running integration tests (heavy dependencies)..."
	python -m pytest tests/neptune_v2/integrations -n auto --durations=0 -q 2>&1

# Run multi-backend E2E tests standalone (requires environment setup)
# NOTE: Prefer running via main Makefile: make test_integration_e2e_minfx_neptune
# which automatically sets up the backend and all environment variables.
test-multi-backend:
	@echo "Running multi-backend E2E tests..."
	@if [ -z "$$NEPTUNE_API_TOKEN_1" ] || [ -z "$$NEPTUNE_API_TOKEN_2" ]; then \
		echo "Error: NEPTUNE_API_TOKEN_1 and NEPTUNE_API_TOKEN_2 must be set."; \
		echo "Use 'make test_integration_e2e_minfx_neptune' from the repo root instead."; \
		exit 1; \
	fi
	python -m pytest tests/neptune_v2/integration/e2e/test_multi_backend.py -v --durations=0

# Run all tests (unit + integrations)
test-all:
	@echo "Running all tests (unit + integrations)..."
	python -m pytest tests/test_minfx.py tests/neptune_v2/unit tests/neptune_v2/integrations -n auto --durations=0 -q

# =============================================================================
# LINTING AND FORMATTING
# =============================================================================

# Run ruff formatter (respects MINATO_QUIET)
fmt:
	@./scripts/fmt.sh

# Check lints (respects MINATO_QUIET)
check:
	@./scripts/check.sh

# Build package for distribution with stripped internal files
# Removes comments, docstrings, and type annotations from internal/ package
build-dist:
	@./scripts/build_dist.sh

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .venv/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# Test installation from built package
install-test:
	@echo "Testing installation from built package..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build' first."; \
		exit 1; \
	fi
	uv pip install dist/minfx-*.tar.gz
	python -c "import minfx; print(f'Successfully installed MinFX version: {minfx.__version__}')"

# Install from built package (production)
install-prod:
	@echo "Installing from built package..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build-dist' first."; \
		exit 1; \
	fi
	uv pip install dist/minfx-*.tar.gz

version:
	cat VERSION

prepare: clean check build-dist test 
	@echo "Preparation complete!"

# Deploy to PyPI
deploy-pypi:
	@echo "Deploying to PyPI..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build-dist' first."; \
		exit 1; \
	fi
	python -m twine upload dist/*

# Run full test cycle (optimized for CI - skip clean for faster incremental builds)
# Original had duplicate install-dev (at start and end) - removed redundancy
# Skip clean: __pycache__ removal adds ~1-2s reimport overhead
# Skip install-test: tarball verification is for releases, not needed for dev testing
all: install-build install-dev check test
	@echo "Full test cycle completed successfully!"

# Full release verification (includes clean + package build/install test)
# Use this before publishing to PyPI
all-release: clean install-build install-dev check test build-dist install-test install-dev
	@echo "Release verification completed successfully!"

# Quick development setup
dev-setup: install-build install-dev
	@echo "Development environment setup complete!"

# Quick test cycle (just run tests, assume deps are installed)
quick-test: test
	@echo "Quick test cycle completed!"
