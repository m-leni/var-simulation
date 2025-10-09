# var-simulation
Aplicación para estimación del Value At Risk e KPIs financieros.

## Features

### Core Functionality
- **Value at Risk (VaR) Calculations**: Historical and parametric VaR methods
- **Portfolio Analysis**: Multi-asset portfolio risk assessment
- **Financial Metrics**: Returns calculation, moving averages, P/E ratios

### Analyst Forecast Integration (New!)
The library now includes comprehensive analyst forecast data from yfinance:

- **Analyst Price Targets**: Get price target forecasts (low, high, mean, median)
- **Earnings Forecasts**: Fetch analyst EPS estimates for current and future periods
- **Revenue Forecasts**: Access analyst revenue projections
- **Growth Estimates**: Retrieve analyst growth rate expectations
- **Forward P/E Ratio**: Calculate forward-looking P/E ratios using analyst estimates

See [notebooks/analyst_forecast_examples.ipynb](notebooks/analyst_forecast_examples.ipynb) for usage examples.

## Development Guide

### Testing

This project includes a comprehensive test suite with 90+ tests covering all critical components.

#### Quick Start

```bash
# Install UV package manager (10-100x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest                                         # All tests
uv run pytest -k "returns"                           # Pattern matching
uv run pytest tests/test_metrics.py                  # Specific file
uv run pytest --cov=src --cov-report=html           # With coverage
```

#### Test Coverage Summary

| Module | Tests | Coverage | Description |
|--------|--------|-----------|-------------|
| metrics.py | 40+ | 90% | VaR calculations, financial metrics |
| data.py | 20+ | 70% | Data fetching, API integrations |
| database.py | 15+ | 85% | SQL operations, data persistence |
| datamodels.py | 10+ | 90% | Data validation models |
| streamlit_app.py | 5+ | 50% | UI components |

#### Project Structure

```
var-simulation/
├── src/                   # Core modules
├── tests/                 # Test suite
│   ├── conftest.py       # Shared fixtures
│   ├── test_*.py         # Test modules
│   ├── README.md         # Detailed examples
│   └── data/             # Test data files
│       ├── aapl_sample.json     # Real AAPL trading data
│       ├── portfolio_sample.json # Multi-stock portfolio
│       └── outputs/             # Expected test outputs
├── streamlit_app.py      # Frontend
└── pytest.ini           # Test configuration
```

#### Test Data Overview

The project includes carefully curated test data:

1. **Sample Market Data** (`tests/data/`)
   - Real AAPL historical prices and volumes
   - Multi-stock portfolio (GOOGL, META, MSFT)
   - Used by test fixtures in `conftest.py`

2. **Expected Outputs** (`tests/data/outputs/`)
   - Verified calculation results
   - Strict tolerances for deterministic functions (1e-10)
   - Flexible tolerances for statistical functions (5-10%)

See [tests/README.md](tests/README.md) for detailed testing documentation.

#### Pre-Merge Checklist

Before merging to the `main` branch, ensure:

##### Code Quality
- [ ] Test suite maintained with 100+ tests
- [ ] Test coverage for all critical modules
- [ ] Fixtures created for common test data
- [ ] External APIs properly mocked
- [ ] All tests pass locally
- [ ] Coverage threshold met (80% overall)
- [ ] No test warnings or errors

##### Infrastructure
- [ ] Test directory structure maintained
- [ ] conftest.py with shared fixtures
- [ ] Test markers configured (unit, integration, api, slow)
- [ ] .gitignore updated for test artifacts
- [ ] Pre-commit hooks configured (optional)

##### CI/CD
- [ ] GitHub Actions workflow passing
- [ ] Coverage reporting configured
- [ ] Security scanning enabled

#### Test Coverage Details

##### Backend Functions (src/metrics.py)
- Calculate returns (log and simple)
- Historical VaR
- Parametric VaR
- Portfolio VaR
- Portfolio returns calculations
- Moving averages (weighted and exponential)
- Cumulative yield calculations

##### Data Layer (src/data.py)
- Stock data fetching (with mocks)
- Stock info retrieval
- Date parameter handling
- Data transformation

##### Database (src/database.py)
- Database creation and schema
- Stock data operations
- Financial data operations
- Schema validation

##### Models (src/datamodels.py)
- Request validation (Ticker, VaR, Portfolio)
- Data model integrity

##### Frontend (streamlit_app.py)
- Basic import validation
- Data validation logic
- Component integration

#### Development Workflow

1. Create feature branch: `git checkout -b dev/feature-name stage`
2. Write tests first: `tests/test_*.py`
3. Implement feature in `src/` or `streamlit_app.py`
4. Run tests: `uv run pytest`
5. Create PR: `dev/feature-name` → `stage`
6. After tests pass: `stage` → `main`

For detailed testing documentation, see [tests/README.md](tests/README.md)

#### Testing Steps Before Merge

```bash
# Clean environment
rm -rf .pytest_cache htmlcov .coverage

# Install dependencies
uv sync --extra dev

# Run all tests
pytest -v

# Check coverage
pytest --cov=src --cov-report=html
```

## Upcoming Features & Implementation Plan

### 1. Risk Profile Assessment System
**Purpose**: Implement user risk aversion measurement and persistence
- [ ] Create risk assessment questionnaire based on standard financial profiling instruments
  - Design questions and scoring system
  - Implement form validation and score calculation
  - Add risk profile categories (Conservative, Moderate, Aggressive, etc.)
- [ ] Develop risk profile persistence
  - Add user profile database schema
  - Implement session management for profile persistence
  - Create profile summary view
- [ ] Add manual risk profile override option
  - Allow direct profile selection
  - Add profile reset functionality
  - Implement profile update tracking

### 2. Enhanced Stock Analysis & Valuation
**Purpose**: Add analyst estimates and advanced P/E analysis
- [x] Integrate analyst estimates data
  - ✓ Add yfinance API functions for forecast data
  - ✓ Implement earnings (EPS) forecast fetching
  - ✓ Add revenue estimates collection
  - ✓ Add growth estimates fetching
  - ✓ Add analyst price targets
- [x] Create P/E analysis module
  - ✓ Calculate forward P/E using analyst estimates
  - ✓ Implement forward P/E ratio function
  - ✓ Add comprehensive forward P/E data extraction
- [ ] Develop price estimation model
  - Create price projection algorithms
  - Implement multiple scenario analysis
  - Add confidence intervals for estimates
- [ ] Add peer comparison functionality

### 3. Returns Database & Precalculation System
**Purpose**: Build efficient returns calculation and storage system
- [ ] Design returns database schema
  - Define yearly returns table structure
  - Add metadata for calculation tracking
  - Implement versioning for updates
- [ ] Create returns calculation pipeline
  - Build batch processing for fetch_financial_data
  - Implement incremental updates
  - Add data validation checks
- [ ] Add expected returns forecasting
  - Implement returns projection models
  - Add market condition adjustments
  - Create update scheduling system

### 4. Portfolio Optimization & Stock Recommendations
**Purpose**: Provide intelligent portfolio enhancement suggestions
- [ ] Develop optimization engine
  - Create risk-reward scoring system
  - Implement correlation analysis
  - Build portfolio diversification metrics
- [ ] Build recommendation system
  - Create stock filtering by risk profile
  - Implement risk-adjusted returns ranking
  - Add sector/industry balance checks
- [ ] Add portfolio simulation
  - Implement what-if analysis
  - Create rebalancing suggestions
  - Add target allocation tracking

### 5. Hedging Strategies System
**Purpose**: Provide automated hedging recommendations
- [ ] Implement hedging instruments analysis
  - Add options strategy evaluation
  - Implement futures contract analysis
  - Create inverse ETF matching
- [ ] Develop hedging recommendations
  - Create cost-benefit analysis
  - Implement strategy ranking
  - Add risk reduction metrics
- [ ] Build hedging simulation
  - Create strategy backtesting
  - Implement cost modeling
  - Add performance tracking

## Technical Dependencies & Prerequisites
- Update database schema for user profiles and returns storage
- Add new API integrations for analyst estimates
- Implement session management system
- Create batch processing pipeline for returns calculation
- Add new visualization components for recommendations

## Data Requirements
- Historical financial data (existing)
- Analyst estimates and forecasts (new)
- Risk assessment questionnaire data (new)
- Hedging instruments data (new)
- Market correlation data (new)

## Integration Points
- Risk profile → Portfolio recommendations
- Returns database → Optimization engine
- Analyst estimates → Valuation models
- Portfolio analysis → Hedging strategies
- User preferences → Session management
