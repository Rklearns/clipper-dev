.PHONY: help install install-dev test lint format clean build publish

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

test:  ## Run tests
	pytest tests/ -v --cov=clipstack --cov-report=html --cov-report=term-missing

test-fast:  ## Run tests without coverage
	pytest tests/ -v

lint:  ## Run linting
	flake8 clipstack/ tests/
	mypy clipstack/

format:  ## Format code with black
	black clipstack/ tests/

format-check:  ## Check code formatting
	black --check clipstack/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

publish:  ## Publish to PyPI (requires twine)
	twine upload dist/*

dev-install: install-dev  ## Install in development mode
	@echo "Development environment ready!"

check: format-check lint test  ## Run all checks

pre-commit: format lint test  ## Run pre-commit checks
