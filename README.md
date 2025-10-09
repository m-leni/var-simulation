# var-simulation
Aplicación para estimación del Value At Risk e KPIs financieros.

## Features

- **Web Interface**: Streamlit-based dashboard for interactive analysis
- **Terminal User Interface (TUI)**: Command-line interface for stock analysis using Textual
- VaR Simulation and Portfolio Analysis
- Real-time stock data fetching
- Financial metrics visualization

## Usage

### Web Interface (Streamlit)

```bash
streamlit run streamlit_app.py
```

### Terminal User Interface (TUI)

The TUI provides a terminal-based interface for stock analysis, perfect for server environments or users who prefer working in the terminal.

```bash
uv run python tui_app.py
```

**Features:**
- Interactive stock ticker input
- Configurable date range (days)
- Real-time data fetching with caching
- **Terminal-based price history plot** (using plotext)
- Stock metrics display (price, volume, period high/low)
- Data table with OHLCV information
- Keyboard shortcuts:
  - `q` - Quit application
  - `r` - Refresh current data
  - `Tab` - Navigate between fields
  - `Enter` - Submit/Fetch data

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
**Purpose**: Implement user risk aversion measurement, persist user profiles, and expose the results for personalization and recommendations.

Status: Planned → Partially implemented (questionnaire stored in `src/params.py`). Next steps provide a clear implementation checklist and acceptance criteria.

Implementation checklist (concrete):
- [ ] Data model & persistence
  - Create a `risk_profiles` table (or add columns to `users`) with fields: id, user_id (nullable for anonymous), score, category, raw_answers (JSON), created_at, updated_at.
  - Provide a small migration script or a `create_risk_profiles_table()` helper in `src/database.py`.
  - Add a Pydantic dataclass / datamodel (e.g., `src/datamodels.py`) for validating submissions and profile payloads.

- [ ] API / backend
  - Add an endpoint (or internal function) to save and retrieve risk profiles: POST `/api/risk-profile` (save) and GET `/api/risk-profile?user_id=<id>` (retrieve). In the Streamlit app, use `insert_to_financial_data`-style helper or a small wrapper.
  - Implement server-side validation and scoring logic that consumes the questionnaire answers and returns: {score:int, category:str, details: {question:answer, ...}}.

- [ ] Frontend (Streamlit)
  - Add a dedicated Risk Profile view (already added): render the questions from `src/params.py`, store answers in `st.session_state`, compute score client-side and then POST to the backend to persist (optional for anonymous users).
  - Add a small summary panel that shows score, category, and suggested allocation ranges (example: Conservative 0-18 → 20% equities, 50% bonds, 30% cash).
  - Provide a "Save profile" button for signed-in users and a "Reset quiz" button that clears the session keys.

- [ ] Scoring & categories
  - Define explicit thresholds and deterministic mapping (e.g., score ≤ 18 => Conservative, 19–32 => Moderate, ≥ 33 => Aggressive). Document these thresholds in README and `src/params.py` as constants.
  - Provide example recommended allocations per category (documented and surfaced in the UI).

- [ ] Tests
  - Unit tests for scoring logic (happy path + edge cases).
  - Integration tests that simulate a full quiz submission and DB persistence (use test DB file under `tests/`).
  - UI-level smoke test (Streamlit) to ensure the view renders and session_state updates.

- [ ] Acceptance criteria
  - Questionnaire loads from `src/params.py` and matches the defined question set.
  - Selecting answers updates the visible score and sticky progress bar immediately.
  - Clicking "Save profile" persists a record in the `risk_profiles` table with correct score and category.
  - Tests cover scoring logic and DB persistence.

Implementation notes / next steps:
- `src/params.py` already centralizes the questions — keep scoring thresholds in that module too.
- Add a small helper in `src/database.py` to create the risk_profiles table and insert profiles.
- If you want, I can implement the DB helper + a small set of unit tests in the next change.

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

<!-- Section 5 removed as requested -->

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
