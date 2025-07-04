# Install build tools
install-build:
	@echo "Installing build tools..."
	pip install build twine

# Install package in development mode
install-dev:
	@echo "Installing package in development mode..."
	pip install -e .

# Run tests
test:
	@echo "Running tests..."
	pip install pytest
	pytest tests/ -v

# Build package for distribution
build:
	@echo "Building package..."
	python -m build

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# Test installation from built package
install-test:
	@echo "Testing installation from built package..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build' first."; \
		exit 1; \
	fi
	pip install dist/minfx-*.tar.gz
	python -c "import minfx; print(f'Successfully installed MinFX version: {minfx.__version__}')"

# Install from built package (production)
install-prod:
	@echo "Installing from built package..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build' first."; \
		exit 1; \
	fi
	pip install dist/minfx-*.tar.gz

# Deploy to PyPI
deploy-pypi:
	@echo "Deploying to PyPI..."
	@if [ ! -d "dist" ]; then \
		echo "No dist directory found. Run 'make build' first."; \
		exit 1; \
	fi
	twine upload dist/*

# Run full test cycle
all: clean install-build test build install-test
	@echo "Full test cycle completed successfully!"

# Quick development setup
dev-setup: install-build install-dev
	@echo "Development environment setup complete!"

# Quick test cycle
quick-test: test build install-test
	@echo "Quick test cycle completed!"

