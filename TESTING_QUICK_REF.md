# Quick Testing Reference

A quick reference guide for common testing commands using UV package manager.

## Setup

```bash
# Install UV (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install from pyproject.toml (recommended)
uv sync --extra dev

# Or install as editable package
uv pip install -e ".[dev]"
```

**Note**: Use `pyproject.toml` for dependency management instead of requirements files.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_metrics.py

# Run specific test class
uv run pytest tests/test_metrics.py::TestCalculateReturns

# Run specific test
uv run pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns_calculation

# Run tests matching pattern
uv run pytest -k "returns"

# Run tests by marker
uv run pytest -m unit          # Only unit tests
uv run pytest -m "not slow"    # Skip slow tests
```

## Coverage

```bash
# Basic coverage
uv run pytest --cov=src --cov=streamlit_app

# Coverage with terminal report
uv run pytest --cov=src --cov=streamlit_app --cov-report=term-missing

# Coverage with HTML report
uv run pytest --cov=src --cov=streamlit_app --cov-report=html
open htmlcov/index.html

# Check coverage threshold
uv run pytest --cov=src --cov=streamlit_app --cov-report=term --cov-fail-under=80
```

## Debugging

```bash
# Show print statements
uv run pytest -s

# Drop into debugger on failure
uv run pytest --pdb

# Show full traceback
uv run pytest --tb=long

# Show local variables on failure
uv run pytest -l

# Run last failed tests only
uv run pytest --lf

# Run failed tests first
uv run pytest --ff
```

## Performance

```bash
# Show slowest tests
uv run pytest --durations=10

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto
```

## Code Quality

```bash
# Linting
uv run flake8 src/ streamlit_app.py --max-line-length=120

# Formatting
uv run black src/ streamlit_app.py --line-length=120

# Check formatting without making changes
uv run black --check src/ streamlit_app.py --line-length=120

# Sort imports
uv run isort src/ streamlit_app.py

# Check import sorting
uv run isort --check-only src/ streamlit_app.py

# Type checking
mypy src/ streamlit_app.py --ignore-missing-imports
```

## Security

```bash
# Security scan
uv run bandit -r src/ streamlit_app.py -ll

# Vulnerability check
safety check

# Detailed security report
uv run bandit -r src/ streamlit_app.py -ll -f json -o security-report.json
```

## Cleaning

```bash
# Remove test artifacts
rm -rf .pytest_cache htmlcov .coverage coverage.xml

# Remove Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## CI/CD

```bash
# Simulate CI locally
uv run pytest --cov=src --cov=streamlit_app --cov-report=xml --cov-report=term
uv run flake8 src/ streamlit_app.py --max-line-length=120
uv run black --check src/ streamlit_app.py --line-length=120
uv run isort --check-only src/ streamlit_app.py
uv run bandit -r src/ streamlit_app.py -ll
```

## Test Markers

Available markers (defined in pytest.ini):
- `unit` - Unit tests (fast, isolated)
- `integration` - Integration tests (slower)
- `slow` - Slow tests (skip in quick runs)
- `api` - API endpoint tests
- `ui` - UI/Streamlit tests

## Common Workflows

### Quick check before commit
```bash
uv run pytest -v --cov=src --cov=streamlit_app --cov-report=term
uv run black --check src/ streamlit_app.py
```

### Full validation
```bash
uv run pytest --cov=src --cov=streamlit_app --cov-report=html
uv run flake8 src/ streamlit_app.py --max-line-length=120
uv run black --check src/ streamlit_app.py
uv run isort --check-only src/ streamlit_app.py
uv run bandit -r src/ streamlit_app.py -ll
```

### Debug failing test
```bash
uv run pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns -v -s --pdb
```

### Check coverage for specific module
```bash
uv run pytest tests/test_metrics.py --cov=src/metrics --cov-report=term-missing
```

## Environment Variables

```bash
# Disable warnings
export PYTHONWARNINGS="ignore"

# Set pytest options
export PYTEST_ADDOPTS="-v --tb=short"

# Parallel execution
export PYTEST_XDIST_AUTO_NUM_WORKERS=4
```

## Useful Combinations

```bash
# Fast feedback loop during development
uv run pytest -x -v  # Stop on first failure, verbose

# Comprehensive test with coverage
uv run pytest -v --cov=src --cov=streamlit_app --cov-report=html --cov-report=term-missing

# CI simulation
uv run pytest --cov=src --cov=streamlit_app --cov-report=xml --cov-fail-under=80

# Debug mode
uv run pytest -v -s --pdb --tb=long -l

# Performance analysis
uv run pytest --durations=0 --cov=src --cov=streamlit_app
```

## Exit Codes

- `0` - All tests passed
- `1` - Tests failed
- `2` - Test execution was interrupted
- `3` - Internal error
- `4` - pytest command line usage error
- `5` - No tests collected

## Tips

1. **Use `-v` for better output**: Shows test names and status
2. **Use `--tb=short` for concise errors**: Less verbose tracebacks
3. **Use `-x` to stop on first failure**: Fast feedback
4. **Use `--lf` to rerun failures**: Quick iteration
5. **Use markers to categorize tests**: Run subsets efficiently
6. **Keep tests independent**: Can run in any order
7. **Mock external dependencies**: Faster, more reliable tests
8. **Use fixtures for common setup**: DRY principle

## Getting Help

```bash
# Pytest help
uv run pytest --help

# Available markers
uv run pytest --markers

# Available fixtures
uv run pytest --fixtures

# Pytest version
uv run pytest --version
```

## Documentation Links

- Full Testing Guide: [TESTING.md](TESTING.md)
- Test Plan: [TEST_PLAN.md](TEST_PLAN.md)
- Test Examples: [tests/README.md](tests/README.md)
- Deployment Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
