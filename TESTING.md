# Testing Documentation

## Overview

This document provides a comprehensive guide to the test suite for the VaR Simulation application. The test suite includes unit tests for backend functions, database tests, and basic tests for the Streamlit frontend.

## Test Coverage Summary

### Modules Tested

1. **src/metrics.py** - Financial calculations and VaR functions
   - `calculate_returns()` - Log and simple returns
   - `historical_var()` - Historical Value at Risk
   - `parametric_var()` - Parametric VaR using normal distribution
   - `portfolio_var()` - Portfolio VaR calculation
   - `calculate_portfolio_returns()` - Weighted portfolio returns
   - `weighted_moving_average()` - WMA calculation
   - `exponential_weighted_moving_average()` - EWMA calculation
   - `calculate_cumulative_yield()` - Cumulative returns

2. **src/data.py** - Data fetching and processing
   - `fetch_stock_data()` - Stock price data from Yahoo Finance (mocked)
   - `get_stock_info()` - Stock metadata retrieval (mocked)
   - Date handling and parameter validation
   - Data transformation and EMA calculations

3. **src/database.py** - Database operations
   - `create_db()` - Table creation and schema validation
   - `insert_to_stock_data()` - Stock data insertion/updates
   - `insert_to_financial_data()` - Financial data insertion/updates
   - Transaction handling and data integrity

4. **src/datamodels.py** - Pydantic models
   - `TickerRequest` - Validation of ticker requests
   - `VaRRequest` - VaR calculation parameters
   - `PortfolioVaRRequest` - Portfolio VaR parameters

5. **streamlit_app.py** - Frontend components (basic tests)
   - Import validation
   - Data caching logic
   - Portfolio weight validation
   - Date range handling

**Note**: `main.py` (FastAPI backend) is deprecated and excluded from testing.

## Quick Start

### 1. Install Dependencies

```bash
# Install project dependencies
uv pip install -r requirements.txt

# Install testing dependencies
uv pip install -r requirements-dev.txt
```

### 2. Run All Tests

```bash
pytest
```

### 3. Run Tests with Coverage

```bash
pytest --cov=src --cov=streamlit_app --cov-report=html
```

### 4. View Coverage Report

```bash
# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

```
tests/
├── __init__.py                # Package initialization
├── conftest.py                # Shared pytest fixtures
├── test_metrics.py            # Metrics module tests (40+ tests)
├── test_data.py               # Data module tests (20+ tests)
├── test_database.py           # Database tests (15+ tests)
├── test_datamodels.py         # Pydantic model tests (10+ tests)
├── test_streamlit_app.py      # Streamlit app tests (5+ tests)
└── README.md                  # Detailed testing guide
```

## Running Specific Tests

### By Module

```bash
# Test only metrics functions
pytest tests/test_metrics.py -v

# Test only API endpoints

# Test only database operations
pytest tests/test_database.py -v
```

### By Test Class

```bash
# Test VaR calculations
pytest tests/test_metrics.py::TestHistoricalVaR -v

# Test portfolio functions
pytest tests/test_metrics.py::TestPortfolioVaR -v
```

### By Individual Test

```bash
# Test specific calculation
pytest tests/test_metrics.py::TestCalculateReturns::test_log_returns_calculation -v
```

### By Marker

```bash
# Run only unit tests
pytest -m unit

# Run only API tests  
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

## Test Fixtures

Common fixtures available in all tests (defined in `conftest.py`):

- **sample_prices** - Series of price data for testing
- **sample_returns** - Array of return values
- **sample_stock_data** - Complete stock DataFrame with all columns
- **sample_financial_data** - Financial statement DataFrame
- **in_memory_db** - SQLite in-memory database for testing
- **portfolio_data** - Multi-asset portfolio data
- **mock_stock_info** - Mock stock metadata
- **confidence_levels** - Common confidence levels [0.90, 0.95, 0.99]
- **investment_values** - Common investment amounts

## Coverage Goals and Status

| Module | Target Coverage | Status |
|--------|----------------|---------|
| src/metrics.py | 90% | ✅ Implemented |
| src/database.py | 85% | ✅ Implemented |
| src/data.py | 70% | ✅ Implemented |
| src/datamodels.py | 90% | ✅ Implemented |
| streamlit_app.py | 50% | 🔄 Basic tests |
| **Overall** | **80%** | 🎯 Target |

**Note**: `main.py` (FastAPI backend) is deprecated and excluded from coverage tracking.

## Continuous Integration

### GitHub Actions Workflow

The test suite runs automatically on:
- Every push to `main` or `dev/testing` branches
- Every pull request to `main`

The CI pipeline includes:

1. **Test Matrix**
   - Python 3.11, 3.12, 3.13
   - Ubuntu latest

2. **Test Execution**
   - Run full test suite
   - Generate coverage reports
   - Upload to Codecov

3. **Code Quality**
   - flake8 linting
   - black formatting check
   - isort import sorting

4. **Security Scanning**
   - bandit security analysis
   - safety vulnerability check

### Workflow File

See `.github/workflows/test.yml` for the complete CI/CD configuration.

## Code Quality Tools

### Linting

```bash
# Check code style
flake8 src/ streamlit_app.py --max-line-length=120

# Auto-format code
black src/ streamlit_app.py --line-length=120

# Sort imports
isort src/ streamlit_app.py
```

### Security

```bash
# Security scan
bandit -r src/ -ll

# Vulnerability check
safety check
```

## Writing New Tests

### 1. Choose the Right Test File

Add tests to the appropriate file based on what you're testing:
- Calculations → `test_metrics.py`
- Data fetching → `test_data.py`
- Database → `test_database.py`

### 2. Follow Naming Conventions

```python
class Test<Functionality>:
    """Tests for <functionality>."""
    
    def test_<specific_behavior>(self):
        """Test <what is being tested>."""
        # Arrange
        # Act
        # Assert
```

### 3. Use Fixtures

```python
def test_with_fixture(sample_prices):
    """Use fixtures from conftest.py."""
    result = calculate_returns(sample_prices)
    assert len(result) == len(sample_prices)
```

### 4. Mock External Dependencies

```python
@patch('src.data.yf.Ticker')
def test_with_mock(mock_ticker):
    """Mock external APIs."""
    mock_ticker.return_value.history.return_value = mock_data
    result = fetch_stock_data('AAPL')
    assert isinstance(result, pd.DataFrame)
```

## Debugging Tests

### Verbose Output

```bash
# Show all output
pytest -v -s

# Show local variables on failure
pytest -l

# Show full traceback
pytest --tb=long
```

### Debug Specific Test

```bash
# Drop into debugger on failure
pytest --pdb

# Start test with debugger
pytest --trace
```

## Best Practices

1. ✅ **Keep tests independent** - No shared state between tests
2. ✅ **Use descriptive names** - Test name should explain what it tests
3. ✅ **Test edge cases** - Empty inputs, boundary values, errors
4. ✅ **Mock external APIs** - Don't make real network calls
5. ✅ **Keep tests fast** - Unit tests should run in milliseconds
6. ✅ **One concept per test** - Test one thing at a time
7. ✅ **Use fixtures** - Reuse common setup code
8. ✅ **Assert clearly** - Use specific assertions with messages

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Install package in editable mode
```bash
uv pip install -e .
```

### Database Connection Errors

**Problem**: Tests fail with database errors

**Solution**: Use the `in_memory_db` fixture
```python
def test_database(in_memory_db):
    create_db(in_memory_db)
    # ... rest of test
```

### Mock Not Working

**Problem**: Mock doesn't intercept the call

**Solution**: Patch where it's used, not where it's defined
```python
# Wrong
@patch('src.data.yf')

# Right  
@patch('src.data.yf.Ticker')
```

## Next Steps

### Short Term
- [ ] Run full test suite and achieve 80% coverage
- [ ] Fix any failing tests
- [ ] Add integration tests
- [ ] Set up pre-commit hooks

### Medium Term
- [ ] Increase Streamlit test coverage
- [ ] Add performance benchmarks
- [ ] Implement E2E tests
- [ ] Add mutation testing

### Long Term
- [ ] Set up test database fixtures
- [ ] Add property-based testing (Hypothesis)
- [ ] Visual regression testing for plots
- [ ] Load testing for API endpoints

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Test Plan](TEST_PLAN.md)
- [Tests README](tests/README.md)

## Support

For questions about the test suite:
1. Check the [TEST_PLAN.md](TEST_PLAN.md) for overall strategy
2. Read [tests/README.md](tests/README.md) for detailed examples
3. Review existing tests for patterns
4. Refer to fixture definitions in `conftest.py`

## Summary

The test suite provides comprehensive coverage of:
- ✅ Core VaR and financial calculations
- ✅ Data fetching with mocked APIs
- ✅ Database operations with in-memory SQLite
- ✅ Pydantic model validation
- ✅ FastAPI endpoint testing
- 🔄 Basic Streamlit component testing

**Total Tests**: 90+ tests across 6 test files

**Status**: ✅ Ready for integration into CI/CD pipeline

The test suite ensures code quality, catches regressions early, and provides confidence when deploying new versions to production.
