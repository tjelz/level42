.PHONY: help clean build install install-dev test lint format check-format type-check security-check docs dist upload-test upload release

help:
	@echo "Available commands:"
	@echo "  clean               Remove build artifacts and cache files"
	@echo "  build               Build the package"
	@echo "  install             Install the package"
	@echo "  install-dev         Install the package in development mode with dev dependencies"
	@echo "  test                Run all tests with coverage"
	@echo "  test-unit           Run unit tests only"
	@echo "  test-integration    Run integration tests with mocks"
	@echo "  test-integration-testnet  Run integration tests with real testnets"
	@echo "  test-integration-suites   Run integration test suites separately"
	@echo "  test-all            Run all tests with HTML coverage report"
	@echo "  lint                Run linting checks"
	@echo "  format              Format code with black"
	@echo "  check-format        Check code formatting"
	@echo "  type-check          Run type checking with mypy"
	@echo "  security-check      Run security checks"
	@echo "  docs                Build documentation"
	@echo "  dist                Build distribution packages"
	@echo "  upload-test         Upload to TestPyPI"
	@echo "  upload              Upload to PyPI"
	@echo "  release             Full release process (test, build, upload)"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python -m build

install:
	pip install .

install-dev:
	pip install -e ".[dev,solana,docs]"

test:
	python -m pytest tests/ -v --cov=x402_agent --cov-report=term-missing

test-unit:
	python -m pytest tests/ -v --cov=x402_agent --cov-report=term-missing --ignore=tests/integration

test-integration:
	python tests/run_integration_tests.py

test-integration-testnet:
	python tests/run_integration_tests.py --testnet

test-integration-suites:
	python tests/run_integration_tests.py --suites

test-all:
	python -m pytest tests/ -v --cov=x402_agent --cov-report=term-missing --cov-report=html

lint:
	python -m flake8 x402_agent tests examples
	python -m black --check x402_agent tests examples

format:
	python -m black x402_agent tests examples

check-format:
	python -m black --check --diff x402_agent tests examples

type-check:
	python -m mypy x402_agent

security-check:
	python -m pip audit

docs:
	cd docs && make html

dist: clean
	python -m build
	python -m twine check dist/*

upload-test: dist
	python -m twine upload --repository testpypi dist/*

upload: dist
	python -m twine upload dist/*

release: test lint type-check security-check dist
	@echo "All checks passed. Ready to upload to PyPI."
	@echo "Run 'make upload' to publish to PyPI"

# Version management
bump-patch:
	@python -c "import re; \
	content = open('x402_agent/__init__.py').read(); \
	version = re.search(r'__version__ = \"([^\"]+)\"', content).group(1); \
	parts = version.split('.'); \
	parts[2] = str(int(parts[2]) + 1); \
	new_version = '.'.join(parts); \
	new_content = re.sub(r'__version__ = \"[^\"]+\"', f'__version__ = \"{new_version}\"', content); \
	open('x402_agent/__init__.py', 'w').write(new_content); \
	print(f'Version bumped to {new_version}')"

bump-minor:
	@python -c "import re; \
	content = open('x402_agent/__init__.py').read(); \
	version = re.search(r'__version__ = \"([^\"]+)\"', content).group(1); \
	parts = version.split('.'); \
	parts[1] = str(int(parts[1]) + 1); \
	parts[2] = '0'; \
	new_version = '.'.join(parts); \
	new_content = re.sub(r'__version__ = \"[^\"]+\"', f'__version__ = \"{new_version}\"', content); \
	open('x402_agent/__init__.py', 'w').write(new_content); \
	print(f'Version bumped to {new_version}')"

bump-major:
	@python -c "import re; \
	content = open('x402_agent/__init__.py').read(); \
	version = re.search(r'__version__ = \"([^\"]+)\"', content).group(1); \
	parts = version.split('.'); \
	parts[0] = str(int(parts[0]) + 1); \
	parts[1] = '0'; \
	parts[2] = '0'; \
	new_version = '.'.join(parts); \
	new_content = re.sub(r'__version__ = \"[^\"]+\"', f'__version__ = \"{new_version}\"', content); \
	open('x402_agent/__init__.py', 'w').write(new_content); \
	print(f'Version bumped to {new_version}')"