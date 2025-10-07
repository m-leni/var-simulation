# Testing Guide

This directory contains the comprehensive test suite for the VaR Simulation application.

## Quick Start

### Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install testing dependencies
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov=main --cov-report=html

# Run specific test file
pytest tests/test_metrics.py -v

# Run specific test class or function
pytest tests/test_metrics.py::TestCalculateReturns -v
pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns_with_series -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_metrics.py          # Tests for src/metrics.py
├── test_data.py             # Tests for src/data.py
├── test_database.py         # Tests for src/database.py
├── test_datamodels.py       # Tests for src/datamodels.py
└── test_api.py              # Tests for FastAPI endpoints
```

## Test Categories

Tests are marked with categories for selective execution:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.api` - API endpoint tests

### Running Specific Categories

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run API tests only
pytest -m api
```

## Coverage

Generate a detailed coverage report:

```bash
# Terminal report
pytest --cov=src --cov=main --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=src --cov=main --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=src --cov=main --cov-report=xml
```

### Coverage Goals

- **Overall**: 80% minimum
- **src/metrics.py**: 90% (critical calculations)
- **src/database.py**: 85%
- **main.py**: 85%
- **src/data.py**: 70% (external API dependencies)

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `sample_prices` - Sample price data for testing
- `sample_returns` - Sample return data
- `sample_stock_data` - Complete stock DataFrame
- `sample_financial_data` - Financial statement data
- `in_memory_db` - SQLite in-memory database
- `portfolio_data` - Multi-asset portfolio data
- `mock_stock_info` - Mock stock information

## Writing Tests

### Test Naming Convention

- Test files: `test_<module>.py`
- Test classes: `Test<Functionality>`
- Test functions: `test_<what_is_being_tested>`

### Example Test

```python
import pytest
from src.metrics import calculate_returns

class TestCalculateReturns:
    """Tests for calculate_returns function."""
    
    def test_log_returns_calculation(self):
        """Test correctness of log returns calculation."""
        prices = pd.Series([100, 110, 105])
        returns = calculate_returns(prices, method='log')
        expected_return_1 = np.log(110/100)
        assert abs(returns.iloc[1] - expected_return_1) < 1e-10
```

### Using Fixtures

```python
def test_with_fixture(sample_prices):
    """Test using a fixture from conftest.py."""
    returns = calculate_returns(sample_prices)
    assert len(returns) == len(sample_prices)
```

### Mocking External APIs

```python
from unittest.mock import patch

@patch('src.data.yf.Ticker')
def test_fetch_stock_data(mock_ticker_class):
    """Test with mocked yfinance API."""
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = mock_dataframe
    mock_ticker_class.return_value = mock_ticker
    
    result = fetch_stock_data('AAPL')
    assert isinstance(result, pd.DataFrame)
```

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `dev/testing` branches
- Every pull request to `main`

See `.github/workflows/test.yml` for CI/CD configuration.

### CI/CD Pipeline

The pipeline includes:
1. **Tests** - Run full test suite on Python 3.11, 3.12, 3.13
2. **Coverage** - Generate and upload coverage reports
3. **Linting** - Check code style with flake8, black, isort
4. **Security** - Scan for vulnerabilities with bandit and safety

## Code Quality

### Linting

```bash
# Check code style
flake8 src/ main.py streamlit_app.py --max-line-length=120

# Format code
black src/ main.py streamlit_app.py --line-length=120

# Sort imports
isort src/ main.py streamlit_app.py

# Type checking
mypy src/ main.py --ignore-missing-imports
```

### Security Scanning

```bash
# Scan for security issues
bandit -r src/ main.py -ll

# Check for known vulnerabilities
safety check
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -s

# Very verbose
pytest -vv

# Show local variables on failure
pytest -l
```

### Debug Specific Test

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### Logging

```bash
# Show log output
pytest --log-cli-level=DEBUG
```

## Performance

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Test Duration

```bash
# Show slowest tests
pytest --durations=10
```

## Best Practices

1. **Keep tests independent** - Each test should be able to run standalone
2. **Use fixtures** - Don't repeat setup code
3. **Mock external dependencies** - Don't make real API calls
4. **Test edge cases** - Test boundary conditions and error cases
5. **Use descriptive names** - Test names should explain what they test
6. **One assertion per test** - Or at least one logical concept
7. **Keep tests fast** - Unit tests should run in milliseconds

## Troubleshooting

### Import Errors

Make sure you're in the project root directory and have installed the package:

```bash
pip install -e .
```

### Database Errors

Tests use in-memory SQLite databases. If you see database errors, check that:
- The `in_memory_db` fixture is being used
- Tables are created before insertion
- Connections are properly closed

### Mock Issues

If mocks aren't working:
- Check the import path matches the actual usage
- Verify the mock is patched where it's used, not where it's defined
- Use `return_value` for functions, not `side_effect`

## Contributing

When adding new functionality:

1. Write tests first (TDD approach recommended)
2. Ensure tests pass: `pytest tests/`
3. Check coverage: `pytest --cov=src --cov-report=term-missing`
4. Run linters: `flake8`, `black`, `isort`
5. Update this README if needed

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
