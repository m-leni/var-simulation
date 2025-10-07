# Test Suite Plan for VaR Simulation Application

## Overview
This document outlines the comprehensive test suite for the VaR simulation application, including unit tests for backend functions, frontend testing, and CI/CD integration.

## Test Structure

```
tests/
├── __init__.py
├── test_metrics.py          # Tests for src/metrics.py functions
├── test_data.py             # Tests for src/data.py functions  
├── test_database.py         # Tests for src/database.py functions
├── test_datamodels.py       # Tests for src/datamodels.py
├── test_api.py              # Tests for main.py FastAPI endpoints
├── test_streamlit_app.py    # Tests for streamlit_app.py components
└── conftest.py              # Shared pytest fixtures
```

## 1. Backend Functions to Test

### 1.1 Metrics Module (`src/metrics.py`)
Priority functions to test:

#### Core VaR Functions
- [x] `calculate_returns(prices, method='log')` 
  - Test with valid price series (pd.Series, np.ndarray, list)
  - Test log returns calculation
  - Test simple returns calculation
  - Test error handling for invalid method
  - Test edge cases (empty data, single value)

- [x] `historical_var(returns, confidence_level, investment_value)`
  - Test with different confidence levels (0.90, 0.95, 0.99)
  - Test with different investment values
  - Test with various return distributions
  - Validate output is positive float
  - Test edge cases (extreme returns, small datasets)

- [x] `parametric_var(returns, confidence_level, investment_value)`
  - Test normal distribution assumption
  - Compare with known statistical values
  - Test with different confidence levels
  - Validate against historical_var for normally distributed data
  - Test edge cases

- [x] `portfolio_var(returns, weights, confidence_level, investment_value, method)`
  - Test both 'historical' and 'parametric' methods
  - Test weight validation
  - Test multi-asset portfolio scenarios
  - Test return dictionary structure
  - Test error handling for invalid method

- [x] `calculate_portfolio_returns(stock_prices, weights)`
  - Test weighted return calculation
  - Test with different number of assets
  - Validate weights and prices alignment
  - Test error handling for mismatched lengths

#### Moving Average Functions
- [x] `weighted_moving_average(data, window, weights)`
  - Test with default weights (linear)
  - Test with custom weights
  - Test window size validation
  - Test edge cases (window larger than data)

- [x] `exponential_weighted_moving_average(data, window, alpha)`
  - Test with default alpha
  - Test with custom alpha values
  - Test alpha validation (0 < alpha <= 1)
  - Compare with pandas ewm implementation

#### Utility Functions
- [x] `calculate_cumulative_yield(prices, method)`
  - Test simple yield calculation
  - Test log-based yield calculation
  - Test with Series and DataFrame inputs
  - Validate percentage output format

### 1.2 Data Module (`src/data.py`)
Priority functions to test:

- [x] `fetch_stock_data(ticker, start_date, days, end_date)`
  - Mock yfinance API calls
  - Test date parameter handling
  - Test data structure/columns
  - Test error handling for invalid tickers
  - Test EMA calculations (ema50, ema200)

- [x] `get_stock_info(ticker)`
  - Mock yfinance info API
  - Test return dictionary structure
  - Test error handling

- [ ] `financial_statement(ticker)` 
  - Mock API responses
  - Test data transformation
  - Test year/period parsing
  - Test error handling

- [ ] `scrape_qqq_holdings()`
  - Mock web scraping
  - Test HTML parsing
  - Test data structure
  - Test error handling for network issues

### 1.3 Database Module (`src/database.py`)

- [x] `create_db(conn)`
  - Test table creation
  - Test idempotency (CREATE IF NOT EXISTS)
  - Verify table schemas
  
- [x] `insert_to_stock_data(df, conn)`
  - Test data insertion
  - Test update/replace logic
  - Test with various DataFrame structures
  - Test error handling

- [x] `insert_to_financial_data(df, ticker, conn)`
  - Test data insertion
  - Test update/replace logic
  - Test ticker column addition
  - Test error handling

### 1.4 Data Models (`src/datamodels.py`)

- [x] `TickerRequest` validation
  - Test required fields
  - Test default values
  - Test field types

- [x] `VaRRequest` validation
  - Test list of floats validation
  - Test confidence level bounds
  - Test default values

- [x] `PortfolioVaRRequest` validation
  - Test list validations
  - Test weight sum validation (handled in API)
  - Test default values

### 1.5 FastAPI Endpoints (`main.py`)

- [x] `POST /` - get_ticker endpoint
  - Test valid ticker requests
  - Test date parameter handling
  - Test response structure (HTML plot)
  - Test error responses

- [x] `POST /var-simulation` - var_simulation endpoint
  - Test VaR calculation with valid data
  - Test both historical and parametric VaR
  - Test confidence level variations
  - Test response structure

- [x] `POST /var-simulation-portfolio` - portfolio_var_simulation endpoint
  - Test portfolio VaR calculation
  - Test weight validation (sum to 1)
  - Test multi-asset scenarios
  - Test response structure with portfolio composition
  - Test error handling

## 2. Frontend Testing (`streamlit_app.py`)

### 2.1 Component Testing
- [ ] Test data loading functions
  - Database connection initialization
  - CSV data loading (sp500_caps.csv)
  - QQQ holdings scraping

- [ ] Test user input handling
  - Ticker selection
  - Date range selection
  - Portfolio weight inputs
  - VaR parameter inputs

- [ ] Test visualization generation
  - Stock analysis plots
  - Financial metrics displays
  - Portfolio analysis outputs

### 2.2 Integration Testing
- [ ] Test complete user workflows
  - Single stock analysis flow
  - Portfolio VaR calculation flow
  - Financial statement retrieval flow

- [ ] Test database interactions
  - Data caching logic
  - Insert/update operations
  - Query operations

### 2.3 UI Testing (Manual/Automated)
- [ ] Visual regression testing (optional)
- [ ] Performance testing for large portfolios
- [ ] Error message display testing

## 3. Test Requirements & Dependencies

### Testing Libraries Needed
```toml
[dependency-groups.test]
pytest = ">=8.0.0"
pytest-cov = ">=4.1.0"
pytest-mock = ">=3.12.0"
pytest-asyncio = ">=0.23.0"
httpx = ">=0.26.0"  # For FastAPI testing
responses = ">=0.24.0"  # For mocking HTTP requests
faker = ">=22.0.0"  # For generating test data
```

### Test Data Requirements
- Sample stock price data (CSV fixtures)
- Sample financial statement data
- Mock API responses
- Database fixtures (SQLite in-memory)

## 4. Coverage Goals

### Minimum Coverage Targets
- **Overall**: 80% coverage
- **src/metrics.py**: 90% coverage (critical calculations)
- **src/data.py**: 70% coverage (external API dependencies)
- **src/database.py**: 85% coverage
- **main.py**: 85% coverage (API endpoints)
- **streamlit_app.py**: 50% coverage (UI components)

### Coverage Exclusions
- External API calls (use mocks)
- Visualization rendering
- Streamlit-specific UI code
- Debug/development-only code

## 5. CI/CD Pipeline Integration

### 5.1 GitHub Actions Workflow (`.github/workflows/test.yml`)

```yaml
name: Test Suite

on:
  push:
    branches: [ main, dev/testing ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock pytest-asyncio httpx responses faker
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov=main --cov-report=xml --cov-report=html --cov-report=term
    
    - name: Upload coverage to Codecov (optional)
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
    
    - name: Check coverage threshold
      run: |
        coverage report --fail-under=80

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.13"
    
    - name: Install linting tools
      run: |
        pip install flake8 black isort mypy
    
    - name: Run linters
      run: |
        flake8 src/ main.py streamlit_app.py --max-line-length=120
        black --check src/ main.py streamlit_app.py
        isort --check-only src/ main.py streamlit_app.py
        mypy src/ main.py --ignore-missing-imports

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit security scan
      run: |
        pip install bandit
        bandit -r src/ main.py -ll
```

### 5.2 Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120]

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

### 5.3 Deployment Gate

Before deployment to `main` branch:
1. All tests must pass
2. Code coverage must be >= 80%
3. No security vulnerabilities (Bandit scan)
4. Linting checks pass
5. Manual review approved

## 6. Test Execution Strategy

### Development Workflow
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_metrics.py -v

# Run with coverage
pytest tests/ --cov=src --cov=main --cov-report=html

# Run only fast tests (exclude slow integration tests)
pytest tests/ -m "not slow"

# Run in parallel (faster)
pytest tests/ -n auto
```

### Test Categories (Markers)
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, may use DB)
- `@pytest.mark.slow` - Slow tests (API calls, etc.)
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.ui` - Streamlit UI tests

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Set up test directory structure
- [x] Create conftest.py with shared fixtures
- [x] Install testing dependencies
- [x] Write tests for core metrics functions (calculate_returns, VaR functions)
- [x] Achieve 80%+ coverage on src/metrics.py

### Phase 2: Backend Coverage (Week 2)
- [x] Write tests for data.py functions
- [x] Write tests for database.py functions
- [x] Write tests for datamodels.py validation
- [x] Write tests for FastAPI endpoints
- [x] Achieve 80%+ overall backend coverage

### Phase 3: Frontend & Integration (Week 3)
- [ ] Write tests for streamlit_app.py components
- [ ] Create integration tests
- [ ] Test end-to-end workflows
- [ ] Performance testing

### Phase 4: CI/CD Setup (Week 4)
- [ ] Create GitHub Actions workflow
- [ ] Set up pre-commit hooks
- [ ] Configure coverage reporting
- [ ] Document testing procedures
- [ ] Create deployment gate checklist

## 8. Success Criteria

- ✅ All tests pass consistently
- ✅ Code coverage >= 80%
- ✅ CI/CD pipeline successfully runs on every push
- ✅ Tests run in < 5 minutes
- ✅ No flaky tests (tests that randomly fail)
- ✅ Documentation is complete
- ✅ Team members can easily add new tests

## 9. Maintenance Plan

- Review and update tests with each new feature
- Monitor test execution time and optimize slow tests
- Keep testing dependencies up to date
- Regular security scans
- Quarterly review of coverage metrics

## 10. Notes

- Mock all external API calls (yfinance, web scraping) to avoid network dependencies
- Use in-memory SQLite databases for database tests
- Parameterize tests where possible to test multiple scenarios
- Keep tests independent (no shared state between tests)
- Use descriptive test names that explain what is being tested
