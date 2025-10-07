# var-simulation
Aplicación para estimación del Value At Risk e KPIs financieros.

## Testing

This project includes a comprehensive test suite with 90+ tests covering backend functions and database operations.

### Quick Start

```bash
# Install dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=streamlit_app --cov-report=html
```

### Test Coverage

- ✅ **src/metrics.py** - VaR calculations and financial metrics (90% coverage target)
- ✅ **src/database.py** - Database operations (85% coverage target)
- ✅ **src/data.py** - Data fetching with mocked APIs (70% coverage target)
- ✅ **src/datamodels.py** - Pydantic validation (90% coverage target)
- 🔄 **streamlit_app.py** - Basic component tests (50% coverage target)

**Note**: `main.py` (FastAPI backend) is deprecated and excluded from testing.

### Branching Strategy

- **`main`**: Production-ready code only
- **`stage`**: Pre-production testing branch
- **`dev/*`**: Feature development branches

**Workflow**: `dev/*` → `stage` (tests run) → `main` (deploy)

### CI/CD

Tests run automatically via GitHub Actions on pushes to `stage` and `dev/*` branches. See [TESTING.md](TESTING.md) for detailed documentation.

**Documentation:**
- [Test Plan](TEST_PLAN.md) - Overall testing strategy
- [Testing Guide](TESTING.md) - How to run and write tests
- [Tests README](tests/README.md) - Detailed test examples

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
- [ ] Integrate analyst estimates data
  - Add API endpoints for forecast data
  - Implement revenue forecast fetching
  - Add EPS estimates collection
- [ ] Create P/E analysis module
  - Calculate historical P/E trends
  - Implement forward P/E projections
  - Add peer comparison functionality
- [ ] Develop price estimation model
  - Create price projection algorithms
  - Implement multiple scenario analysis
  - Add confidence intervals for estimates

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
