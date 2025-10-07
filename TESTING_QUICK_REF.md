# Quick Testing Reference

A quick reference guide for common testing commands.

## Setup

```bash
# One-time setup
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_metrics.py

# Run specific test class
pytest tests/test_metrics.py::TestCalculateReturns

# Run specific test
pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns_calculation

# Run tests matching pattern
pytest -k "returns"

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Skip slow tests
```

## Coverage

```bash
# Basic coverage
pytest --cov=src --cov=streamlit_app

# Coverage with terminal report
pytest --cov=src --cov=streamlit_app --cov-report=term-missing

# Coverage with HTML report
pytest --cov=src --cov=streamlit_app --cov-report=html
open htmlcov/index.html

# Check coverage threshold
pytest --cov=src --cov=streamlit_app --cov-report=term --cov-fail-under=80
```

## Debugging

```bash
# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show full traceback
pytest --tb=long

# Show local variables on failure
pytest -l

# Run last failed tests only
pytest --lf

# Run failed tests first
pytest --ff
```

## Performance

```bash
# Show slowest tests
pytest --durations=10

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Code Quality

```bash
# Linting
flake8 src/ streamlit_app.py --max-line-length=120

# Formatting
black src/ streamlit_app.py --line-length=120

# Check formatting without making changes
black --check src/ streamlit_app.py --line-length=120

# Sort imports
isort src/ streamlit_app.py

# Check import sorting
isort --check-only src/ streamlit_app.py

# Type checking
mypy src/ streamlit_app.py --ignore-missing-imports
```

## Security

```bash
# Security scan
bandit -r src/ streamlit_app.py -ll

# Vulnerability check
safety check

# Detailed security report
bandit -r src/ streamlit_app.py -ll -f json -o security-report.json
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
pytest --cov=src --cov=streamlit_app --cov-report=xml --cov-report=term
flake8 src/ streamlit_app.py --max-line-length=120
black --check src/ streamlit_app.py --line-length=120
isort --check-only src/ streamlit_app.py
bandit -r src/ streamlit_app.py -ll
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
pytest -v --cov=src --cov=streamlit_app --cov-report=term
black --check src/ streamlit_app.py
```

### Full validation
```bash
pytest --cov=src --cov=streamlit_app --cov-report=html
flake8 src/ streamlit_app.py --max-line-length=120
black --check src/ streamlit_app.py
isort --check-only src/ streamlit_app.py
bandit -r src/ streamlit_app.py -ll
```

### Debug failing test
```bash
pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns -v -s --pdb
```

### Check coverage for specific module
```bash
pytest tests/test_metrics.py --cov=src/metrics --cov-report=term-missing
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
pytest -x -v  # Stop on first failure, verbose

# Comprehensive test with coverage
pytest -v --cov=src --cov=streamlit_app --cov-report=html --cov-report=term-missing

# CI simulation
pytest --cov=src --cov=streamlit_app --cov-report=xml --cov-fail-under=80

# Debug mode
pytest -v -s --pdb --tb=long -l

# Performance analysis
pytest --durations=0 --cov=src --cov=streamlit_app
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
pytest --help

# Available markers
pytest --markers

# Available fixtures
pytest --fixtures

# Pytest version
pytest --version
```

## Documentation Links

- Full Testing Guide: [TESTING.md](TESTING.md)
- Test Plan: [TEST_PLAN.md](TEST_PLAN.md)
- Test Examples: [tests/README.md](tests/README.md)
- Deployment Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
