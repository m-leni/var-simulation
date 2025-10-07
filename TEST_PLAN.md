# Test Suite Plan for VaR Simulation Application

## Overview
This document outlines the comprehensive test suite for the VaR simulation application, including unit tests for backend functions, frontend testing, and CI/CD integration.

## Branching Strategy

The project follows a three-tier branching model:

- **`main`**: Production-ready code only. Protected branch that receives merges only from `stage` after all tests pass.
- **`stage`**: Pre-production testing branch. All tests must pass here before merging to `main`.
- **`dev/*`**: Feature development branches. All new features and changes are developed here (e.g., `dev/testing`, `dev/new-feature`).

**Workflow**:
1. Create feature branch from `stage`: `git checkout -b dev/feature-name stage`
2. Develop and test on feature branch
3. Create PR to merge `dev/feature-name` → `stage`
4. CI/CD runs tests on `stage`
5. Once stable, create PR to merge `stage` → `main`
6. Deploy from `main`

## Test Structure

```
tests/
├── __init__.py
├── test_metrics.py          # Tests for src/metrics.py functions
├── test_data.py             # Tests for src/data.py functions  
├── test_database.py         # Tests for src/database.py functions
├── test_datamodels.py       # Tests for src/datamodels.py
├── test_streamlit_app.py    # Tests for streamlit_app.py components
└── conftest.py              # Shared pytest fixtures
```

**Note**: `main.py` (FastAPI backend) is deprecated and excluded from testing.

## 1. Backend Functions to Test

### 1.1 Metrics Module (`src/metrics.py`)
Priority functions to test:

#### Core VaR Functions

**`calculate_returns(prices, method='log')`**
- [x] **Test with valid price series**: Verify function accepts pd.Series, np.ndarray, and list inputs
  - **Why**: Ensures flexibility in input types from different data sources
  - **How**: Pass each type and verify output is consistent pd.Series
  - **Expected**: All input types return same structure with correct calculations
  
- [x] **Test log returns calculation**: Verify ln(P_t / P_{t-1}) formula
  - **Why**: Log returns are preferred for VaR due to time-additive property
  - **How**: Calculate manually for known prices and compare with function output
  - **Expected**: Returns match manual calculation within floating-point precision (1e-10)
  
- [x] **Test simple returns calculation**: Verify (P_t - P_{t-1}) / P_{t-1} formula
  - **Why**: Simple returns are more intuitive for reporting
  - **How**: Use known price changes and verify percentage calculations
  - **Expected**: Returns exactly match expected percentages
  
- [x] **Test error handling for invalid method**: Ensure proper exception for unsupported methods
  - **Why**: Prevents silent failures with incorrect method names
  - **How**: Pass invalid method string (e.g., 'exponential')
  - **Expected**: ValueError with descriptive message
  
- [x] **Test edge cases**: Handle empty data, single value, NaN values
  - **Why**: Real data may have missing or insufficient values
  - **How**: Pass edge case inputs and verify graceful handling
  - **Expected**: Appropriate handling without crashes (NaN for first value, etc.)

**`historical_var(returns, confidence_level, investment_value)`**
- [x] **Test with different confidence levels**: Verify VaR increases with confidence (90%, 95%, 99%)
  - **Why**: Higher confidence should yield higher VaR (more conservative estimate)
  - **How**: Calculate VaR at multiple confidence levels with same data
  - **Expected**: VaR_99% > VaR_95% > VaR_90%
  - **Reasoning**: At 99% confidence, we capture more extreme tail events
  
- [x] **Test with different investment values**: Verify linear scaling
  - **Why**: VaR should scale proportionally with portfolio size
  - **How**: Calculate VaR for $10K and $20K with same returns
  - **Expected**: VaR($20K) = 2 × VaR($10K) within 1% tolerance
  - **Reasoning**: VaR is linear in portfolio value
  
- [x] **Test with various return distributions**: Normal, skewed, heavy-tailed
  - **Why**: Real returns are rarely perfectly normal
  - **How**: Generate synthetic returns with known properties
  - **Expected**: VaR reflects actual percentile regardless of distribution
  
- [x] **Validate output is positive float**: Type and sign checking
  - **Why**: VaR represents potential loss (always positive)
  - **How**: Assert isinstance(var, float) and var >= 0
  - **Expected**: Always returns non-negative float
  
- [x] **Test edge cases**: Extreme returns, small datasets (n<30)
  - **Why**: Insufficient data affects reliability
  - **How**: Pass minimal samples (5-10 returns)
  - **Expected**: Function completes but results may be less reliable

**`parametric_var(returns, confidence_level, investment_value)`**
- [x] **Test normal distribution assumption**: Compare with theoretical values
  - **Why**: Parametric VaR assumes returns are normally distributed
  - **How**: Generate N(μ=0, σ=0.01) returns, compare VaR to 1.645σ (95%)
  - **Expected**: Within 15% of theoretical value (1.645 × 0.01 × investment)
  - **Reasoning**: Monte Carlo approximation has sampling error
  
- [x] **Compare with known statistical values**: Verify z-scores
  - **Why**: Ensures correct implementation of z-score lookups
  - **How**: For 95% confidence, z-score should be ~1.645
  - **Expected**: VaR = investment × (μ + z × σ) matches manual calculation
  
- [x] **Test with different confidence levels**: Verify z-score increases
  - **Why**: Different confidence levels use different z-scores
  - **How**: Calculate 90%, 95%, 99% and verify ordering
  - **Expected**: VaR increases monotonically with confidence
  
- [x] **Validate against historical_var**: Should be similar for normal data
  - **Why**: Both methods should converge for normally distributed returns
  - **How**: Generate N(0, 0.01) returns, compare both methods
  - **Expected**: Within 20% of each other (allows for sampling error)
  
- [x] **Test edge cases**: Non-normal distributions
  - **Why**: Parametric VaR can underestimate risk for heavy tails
  - **How**: Use returns with known skewness/kurtosis
  - **Expected**: Function completes, but may differ from historical VaR

**`portfolio_var(returns, weights, confidence_level, investment_value, method)`**
- [x] **Test both 'historical' and 'parametric' methods**: Verify both work correctly
  - **Why**: Users need choice between methods depending on data properties
  - **How**: Pass same portfolio data to both methods
  - **Expected**: Both return valid VaR values, parametric assumes normality
  
- [x] **Test weight validation**: Ensure weights are non-negative and reasonable
  - **Why**: Negative weights (shorting) have different risk properties
  - **How**: Check weights within [0, 1] and sum ≈ 1
  - **Expected**: Warning or error for invalid weights
  
- [x] **Test multi-asset portfolio scenarios**: 2, 3, 5+ assets
  - **Why**: Portfolio VaR accounts for correlations between assets
  - **How**: Create portfolios with varying correlations
  - **Expected**: Diversified portfolio has lower VaR than sum of individual VaRs
  - **Reasoning**: Correlation < 1 provides diversification benefit
  
- [x] **Test return dictionary structure**: If method returns dict
  - **Why**: API contract must be consistent
  - **How**: Verify keys and value types
  - **Expected**: Dict with expected keys or single float value
  
- [x] **Test error handling for invalid method**: 'invalid' should raise error
  - **Why**: Prevents silent failures
  - **How**: Pass method='invalid'
  - **Expected**: ValueError with clear message

**`calculate_portfolio_returns(stock_prices, weights)`**
- [x] **Test weighted return calculation**: Verify R_p = Σ(w_i × R_i)
  - **Why**: Core portfolio theory calculation
  - **How**: Manual calculation for 2-3 assets, compare with function
  - **Expected**: Exact match within floating-point precision
  - **Reasoning**: Portfolio return is weighted average of component returns
  
- [x] **Test with different number of assets**: 1, 2, 5, 10 assets
  - **Why**: Function should scale to any portfolio size
  - **How**: Generate portfolios of varying sizes
  - **Expected**: Correct calculation regardless of portfolio size
  
- [x] **Validate weights and prices alignment**: Same length, correct mapping
  - **Why**: Misalignment causes incorrect calculations
  - **How**: Verify shape compatibility before calculation
  - **Expected**: Error if lengths don't match
  
- [x] **Test error handling for mismatched lengths**: weights ≠ len(stocks)
  - **Why**: Common user error that should be caught
  - **How**: Pass 3 weights for 2 stocks
  - **Expected**: ValueError with descriptive message

#### Moving Average Functions

**`weighted_moving_average(data, window, weights)`**
- [x] **Test with default weights (linear)**: More weight on recent data
  - **Why**: Default should be sensible for most use cases
  - **How**: Verify default assigns increasing weights [1, 2, 3, ...]
  - **Expected**: Recent values have higher impact on average
  - **Reasoning**: Recent data is often more relevant for forecasting
  
- [x] **Test with custom weights**: User-specified weighting scheme
  - **Why**: Advanced users may want specific weighting
  - **How**: Pass custom weights like [0.5, 0.3, 0.2]
  - **Expected**: Average calculated with exact custom weights
  
- [x] **Test window size validation**: window >= 1
  - **Why**: Window of 0 or negative is undefined
  - **How**: Pass window=0, window=-1
  - **Expected**: ValueError
  
- [x] **Test edge cases**: Window larger than data length
  - **Why**: Not enough data for calculation
  - **How**: Pass window=100 with only 10 data points
  - **Expected**: NaN for initial values, or appropriate handling

**`exponential_weighted_moving_average(data, window, alpha)`**
- [x] **Test with default alpha**: α = 2/(window + 1)
  - **Why**: Standard EWMA formula from literature
  - **How**: Verify default alpha calculation
  - **Expected**: Alpha matches formula: 2/(window + 1)
  - **Reasoning**: Provides smoothing equivalent to simple moving average
  
- [x] **Test with custom alpha values**: User-specified decay rate
  - **Why**: Different alpha values provide different smoothing
  - **How**: Test with alpha = 0.1, 0.5, 0.9
  - **Expected**: Higher alpha gives more weight to recent values
  
- [x] **Test alpha validation**: 0 < α ≤ 1
  - **Why**: Alpha outside this range is undefined
  - **How**: Pass alpha=0, alpha=1.5
  - **Expected**: ValueError for invalid alpha
  
- [x] **Compare with pandas ewm implementation**: Verify consistency
  - **Why**: Should match industry-standard implementation
  - **How**: Compare output with pd.Series.ewm()
  - **Expected**: Results match pandas within numerical precision

#### Utility Functions

**`calculate_cumulative_yield(prices, method)`**
- [x] **Test simple yield calculation**: (P_t - P_0) / P_0 × 100
  - **Why**: Intuitive measure of total return
  - **How**: Price goes 100 → 110 → 120
  - **Expected**: Yields of 0%, 10%, 20%
  - **Reasoning**: Relative to starting price, not previous period
  
- [x] **Test log-based yield calculation**: (exp(Σln(P_t/P_{t-1})) - 1) × 100
  - **Why**: Proper compounding of log returns
  - **How**: Calculate cumulative sum of log returns
  - **Expected**: Matches simple for small returns, diverges for large
  
- [x] **Test with Series and DataFrame inputs**: Both should work
  - **Why**: Flexibility for single or multiple series
  - **How**: Pass pd.Series and pd.DataFrame
  - **Expected**: Series returns Series, DataFrame returns DataFrame
  
- [x] **Validate percentage output format**: Results in percent, not decimal
  - **Why**: User-friendly display (20% not 0.20)
  - **How**: Verify values are multiplied by 100
  - **Expected**: Values in range -100 to +∞ for typical returns

### 1.2 Data Module (`src/data.py`)
Priority functions to test:

**`fetch_stock_data(ticker, start_date, days, end_date)`**
- [x] **Mock yfinance API calls**: Isolate from external dependencies
  - **Why**: Tests should not depend on external APIs (reliability, speed, rate limits)
  - **How**: Use `@patch('src.data.yf.Ticker')` to mock yfinance responses
  - **Expected**: Test runs without network calls, predictable results
  - **Reasoning**: Unit tests should be deterministic and fast
  
- [x] **Test date parameter handling**: start_date, end_date, days
  - **Why**: Multiple ways to specify date ranges need consistent handling
  - **How**: Test with string dates ('2024-01-01'), date objects, days parameter
  - **Expected**: All formats produce correct date range for API call
  - **Edge cases**: Start > end should error, days < 0 should error
  
- [x] **Test data structure/columns**: Verify expected DataFrame schema
  - **Why**: Downstream code depends on specific columns
  - **How**: Assert presence of Date, Ticker, Open, High, Low, Close, Volume, etc.
  - **Expected**: All required columns present with correct dtypes
  - **Schema**: ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'ema50', 'ema200', 'yield']
  
- [x] **Test error handling for invalid tickers**: Graceful failure
  - **Why**: Users may enter non-existent ticker symbols
  - **How**: Mock yfinance to return empty DataFrame for 'INVALID'
  - **Expected**: Return empty DataFrame or raise informative error
  - **User experience**: Clear error message, no crash
  
- [x] **Test EMA calculations**: Verify ema50 and ema200 columns
  - **Why**: Technical indicators used in analysis must be correct
  - **How**: Generate known price series, calculate EMA manually, compare
  - **Expected**: EMA values match pandas.ewm(span=50/200) within precision
  - **Reasoning**: EMA smooths noise and identifies trends

**`get_stock_info(ticker)`**
- [x] **Mock yfinance info API**: Isolate from external dependencies
  - **Why**: Company info changes rarely, no need for real API calls
  - **How**: Mock ticker.info to return dict with company metadata
  - **Expected**: Test runs instantly without network
  
- [x] **Test return dictionary structure**: Verify expected keys
  - **Why**: Code expects specific keys like 'sector', 'marketCap', etc.
  - **How**: Assert presence of critical keys in returned dict
  - **Expected keys**: symbol, shortName, sector, industry, marketCap, currentPrice
  
- [x] **Test error handling**: Missing data, API failures
  - **Why**: Not all tickers have complete info
  - **How**: Mock empty/partial info responses
  - **Expected**: Graceful handling, return partial data or None

**`financial_statement(ticker)`** (Future implementation)
- [ ] **Mock API responses**: Isolate from external financial data APIs
  - **Why**: Financial data APIs have rate limits and costs
  - **How**: Mock fetch_financial_data to return known financial statements
  - **Expected**: Test uses mocked data, no API calls
  
- [ ] **Test data transformation**: Raw API → standardized format
  - **Why**: Different APIs return different formats
  - **How**: Provide sample API response, verify transformation
  - **Expected**: Consistent output format regardless of source
  - **Output**: DataFrame with columns [Year, Total Revenue, EBITDA, Free Cash Flow, etc.]
  
- [ ] **Test year/period parsing**: Handle quarterly vs annual data
  - **Why**: Financial data comes in different periods
  - **How**: Test with Q1 2024, FY 2023 formats
  - **Expected**: Correctly extract year and period
  
- [ ] **Test error handling**: Missing data, invalid ticker
  - **Why**: Not all companies have complete financial history
  - **How**: Mock scenarios with missing quarters
  - **Expected**: Fill with NaN or interpolate appropriately

**`scrape_qqq_holdings()`** (Future implementation)
- [ ] **Mock web scraping**: Isolate from website changes
  - **Why**: Website structure can change, breaking scraper
  - **How**: Mock requests.get() to return known HTML
  - **Expected**: Test independent of actual website
  
- [ ] **Test HTML parsing**: Extract table correctly
  - **Why**: BeautifulSoup parsing can be fragile
  - **How**: Provide sample HTML with holdings table
  - **Expected**: Extract ticker symbols, weights, company names
  
- [ ] **Test data structure**: Verify DataFrame schema
  - **Why**: Downstream code expects specific format
  - **How**: Assert columns [Ticker, Weight, Company Name]
  - **Expected**: Weight as float (0-1), Ticker as string
  
- [ ] **Test error handling for network issues**: Timeouts, 404s
  - **Why**: Network can be unreliable
  - **How**: Mock connection errors
  - **Expected**: Retry logic or graceful failure with cached data

### 1.3 Database Module (`src/database.py`)

**`create_db(conn)`**
- [x] **Test table creation**: Verify both tables are created
  - **Why**: Application depends on specific database schema
  - **How**: Call create_db, query sqlite_master for table names
  - **Expected**: Tables 'daily_stock_price' and 'financial_data' exist
  - **Reasoning**: Schema must match INSERT/SELECT statements in code
  
- [x] **Test idempotency (CREATE IF NOT EXISTS)**: Multiple calls safe
  - **Why**: Function may be called on startup every time
  - **How**: Call create_db twice, verify no errors
  - **Expected**: Second call has no effect, no duplicate tables
  - **Database**: SQLite CREATE TABLE IF NOT EXISTS ensures idempotency
  
- [x] **Verify table schemas**: Column names and types correct
  - **Why**: Query code expects specific columns
  - **How**: Use PRAGMA table_info() to inspect schema
  - **Expected daily_stock_price**: Date, Ticker, Open, High, Low, Close, Volume, Dividends, ema50, ema200, yield
  - **Expected financial_data**: Ticker, Year, Total Revenue, Total Expenses, Gross Profit, EBITDA, etc.
  - **Reasoning**: Type mismatches cause runtime errors

**`insert_to_stock_data(df, conn)`**
- [x] **Test data insertion**: New data added to table
  - **Why**: Core functionality for caching stock data
  - **How**: Insert DataFrame, query table to verify rows present
  - **Expected**: Row count matches DataFrame length
  
- [x] **Test update/replace logic**: Old data replaced with new
  - **Why**: Avoid duplicates when refreshing data
  - **How**: Insert same ticker/date range twice with different values
  - **Expected**: Second INSERT deletes old data first, only new data present
  - **Implementation**: DELETE WHERE ticker AND date range, then INSERT
  
- [x] **Test with various DataFrame structures**: Different column orders, extra columns
  - **Why**: Input DataFrame format may vary
  - **How**: Test with columns in different orders, with/without optional columns
  - **Expected**: Function handles variations gracefully
  
- [x] **Test error handling**: Missing required columns, wrong types
  - **Why**: Invalid data should not crash application
  - **How**: Pass DataFrame without 'Ticker' column
  - **Expected**: Clear error message indicating missing column

**`insert_to_financial_data(df, ticker, conn)`**
- [x] **Test data insertion**: Financial statements saved correctly
  - **Why**: Users need access to historical financials
  - **How**: Insert sample financial data, query back
  - **Expected**: Data matches input within floating-point precision
  
- [x] **Test update/replace logic**: Old financials replaced
  - **Why**: Quarterly updates require replacing old data
  - **How**: Insert data for AAPL, then insert new data for AAPL
  - **Expected**: Only latest data present (DELETE before INSERT)
  
- [x] **Test ticker column addition**: Ticker prepended to DataFrame
  - **Why**: Financial data doesn't originally include ticker
  - **How**: Pass DataFrame without Ticker column
  - **Expected**: Function adds Ticker column automatically
  - **Implementation**: `df.insert(loc=0, column='Ticker', value=ticker)`
  
- [x] **Test error handling**: Malformed data, missing years
  - **Why**: Financial data may have gaps
  - **How**: Pass DataFrame with NaN values
  - **Expected**: NaN values stored as NULL in database

### 1.4 Data Models (`src/datamodels.py`)

**`TickerRequest` validation**
- [x] **Test required fields**: ticker must be present
  - **Why**: Pydantic enforces data contracts at API boundary
  - **How**: Create TickerRequest without ticker
  - **Expected**: ValidationError with message about missing field
  
- [x] **Test default values**: days defaults to 365
  - **Why**: Sensible defaults improve UX
  - **How**: Create TickerRequest with only ticker
  - **Expected**: days=365, end_date=None
  
- [x] **Test field types**: ticker is string, days is int
  - **Why**: Type safety prevents bugs
  - **How**: Try to pass days="invalid"
  - **Expected**: ValidationError

**`VaRRequest` validation**
- [x] **Test list of floats validation**: returns must be numeric array
  - **Why**: VaR calculation requires numeric returns
  - **How**: Pass returns=[0.01, -0.02, 0.03]
  - **Expected**: Validation passes
  
- [x] **Test confidence level bounds**: Should be between 0 and 1
  - **Why**: Confidence level is probability (0-100% or 0-1)
  - **How**: Try confidence_level=1.5
  - **Expected**: May pass validation (business logic checks elsewhere)
  - **Note**: Consider adding validator for 0 < CL < 1
  
- [x] **Test default values**: CL=0.95, investment=1.0
  - **Why**: 95% is industry standard for VaR
  - **How**: Create VaRRequest with only returns
  - **Expected**: confidence_level=0.95, investment_value=1.0

**`PortfolioVaRRequest` validation**
- [x] **Test list validations**: tickers and weights are lists
  - **Why**: Portfolio requires multiple assets
  - **How**: Pass tickers=['AAPL', 'GOOGL'], weights=[0.6, 0.4]
  - **Expected**: Validation passes
  
- [x] **Test weight sum validation**: Handled in business logic
  - **Why**: Weights should sum to 1.0 (or 100%)
  - **How**: Pass weights=[0.6, 0.5] (sum=1.1)
  - **Expected**: Pydantic allows, API layer validates
  - **Future**: Add Pydantic validator: @validator('weights')
  
- [x] **Test default values**: days=252, CL=0.95, method='historical'
  - **Why**: 252 trading days ≈ 1 year
  - **How**: Create request with only tickers and weights
  - **Expected**: All defaults applied correctly

## 2. Frontend Testing (`streamlit_app.py`)

### 2.1 Component Testing

**Data loading functions**
- [ ] **Test database connection initialization**: CONN = sql.connect("database.db")
  - **Why**: Application depends on persistent database connection
  - **How**: Mock sql.connect, verify create_db called
  - **Expected**: Connection established without errors
  - **Edge cases**: Database locked, permissions issues
  
- [ ] **Test CSV data loading**: sp500_caps.csv
  - **Why**: SP500 data used for stock selection UI
  - **How**: Mock pd.read_csv to return sample DataFrame
  - **Expected**: DataFrame with expected columns (Symbol, Name, MarketCap)
  - **Reasoning**: File must exist and have correct format
  
- [ ] **Test QQQ holdings scraping**: scrape_qqq_holdings()
  - **Why**: Users select from QQQ constituents
  - **How**: Mock scraping function to return sample holdings
  - **Expected**: DataFrame with Ticker, Weight columns
  - **Error handling**: Network failure, parse errors

**User input handling**
- [ ] **Test ticker selection**: Dropdown/text input validation
  - **Why**: Invalid ticker breaks data fetching
  - **How**: Test st.text_input validation logic
  - **Expected**: Converts to uppercase, rejects empty/invalid
  - **User experience**: Clear error messages
  
- [ ] **Test date range selection**: Start date < end date
  - **Why**: Invalid date range crashes queries
  - **How**: Test date validation: start_date >= end_date should error
  - **Expected**: st.error() called with descriptive message
  - **Implementation**: if start_date >= end_date: st.error("...")
  
- [ ] **Test portfolio weight inputs**: Sum to 1.0, non-negative
  - **Why**: Invalid weights produce incorrect VaR
  - **How**: Test weight validation logic
  - **Expected**: Warning if sum ≠ 1.0, error if negative weights
  - **User feedback**: Display sum, allow normalization
  
- [ ] **Test VaR parameter inputs**: Confidence level, investment amount
  - **Why**: Parameters must be within valid ranges
  - **How**: Test 0 < confidence_level < 1, investment > 0
  - **Expected**: Slider constraints enforce ranges
  - **UI**: st.slider(min_value=0.8, max_value=0.99)

**Visualization generation**
- [ ] **Test stock analysis plots**: plot_stock_analysis() integration
  - **Why**: Charts are primary user interface
  - **How**: Mock plotly figure generation
  - **Expected**: Figure renders without errors
  - **Components**: Price chart, volume bars, EMA lines
  
- [ ] **Test financial metrics displays**: DataFrames with styling
  - **Why**: Financial statements must be readable
  - **How**: Verify DataFrame formatting and styling
  - **Expected**: Numbers formatted as currency, color gradients applied
  - **Styling**: .style.background_gradient(cmap='RdYlGn')
  
- [ ] **Test portfolio analysis outputs**: VaR results, exposure tables
  - **Why**: Portfolio analytics are main application value
  - **How**: Mock VaR calculations, verify display
  - **Expected**: VaR displayed with currency formatting
  - **Components**: Risk metrics table, sector exposure chart

### 2.2 Integration Testing

**Complete user workflows**
- [ ] **Test single stock analysis flow**: Select ticker → View data → Calculate VaR
  - **Why**: End-to-end validation of core feature
  - **Steps**: 
    1. User enters "AAPL"
    2. Selects date range (last 1 year)
    3. Clicks "Fetch stock data"
    4. Views price chart
    5. Calculates VaR at 95% confidence
  - **Expected**: All steps complete without errors
  - **Data flow**: Input → fetch_stock_data() → plot → VaR calculation
  
- [ ] **Test portfolio VaR calculation flow**: Multi-stock portfolio analysis
  - **Why**: Validates portfolio features work together
  - **Steps**:
    1. Select number of assets (3)
    2. Enter tickers: AAPL, GOOGL, MSFT
    3. Assign weights: 0.5, 0.3, 0.2
    4. Set VaR parameters (252 days, 95% CL)
    5. Calculate portfolio VaR
  - **Expected**: Portfolio VaR < sum of individual VaRs (diversification benefit)
  - **Validation**: Correlation matrix shows diversification
  
- [ ] **Test financial statement retrieval flow**: Get financials → View trends
  - **Why**: Financial analysis is key feature
  - **Steps**:
    1. Select ticker
    2. Click "Get Financial Data"
    3. View revenue, EBITDA, FCF trends
    4. Analyze YoY growth rates
  - **Expected**: Financial data displays with year-over-year comparisons
  - **Calculations**: ((current - previous) / previous) × 100

**Database interactions**
- [ ] **Test data caching logic**: Avoid redundant API calls
  - **Why**: Reduces latency and API rate limit issues
  - **How**: Mock database queries, verify cache hit/miss logic
  - **Expected**: 
    - Cache hit: Data loaded from DB without API call
    - Cache miss: Data fetched from API, then inserted to DB
  - **Implementation**:
    ```python
    df = pd.read_sql("SELECT * FROM daily_stock_price WHERE ...", conn)
    if df.empty or df.Date.min() != expected_start:
        df = fetch_stock_data(...)  # API call
        insert_to_stock_data(df, conn)  # Cache
    ```
  
- [ ] **Test insert/update operations**: New data overwrites old
  - **Why**: Stale data misleads users
  - **How**: Insert data twice, verify only latest present
  - **Expected**: Second insert replaces first (DELETE then INSERT)
  
- [ ] **Test query operations**: Efficient date range queries
  - **Why**: Large databases need indexed queries
  - **How**: Query with date filters, measure performance
  - **Expected**: Query completes in <100ms
  - **Optimization**: Index on (Ticker, Date) for fast filtering

### 2.3 UI Testing (Manual/Automated)

**Visual regression testing (optional)**
- [ ] **Screenshot comparison**: Detect unintended UI changes
  - **Why**: Refactoring shouldn't break layouts
  - **How**: Capture screenshots before/after, diff them
  - **Tools**: Percy, Chromatic, or manual review
  - **Expected**: Layouts remain consistent
  
**Performance testing for large portfolios**
- [ ] **Test with 20+ assets**: Response time under 5 seconds
  - **Why**: Users may analyze large portfolios
  - **How**: Create portfolio with 20-50 stocks, measure calculation time
  - **Expected**: VaR calculation completes in <5s
  - **Optimization**: Vectorized operations, caching
  
**Error message display testing**
- [ ] **Test error scenarios**: Invalid input, API failures, DB errors
  - **Why**: Errors should be user-friendly
  - **How**: Trigger various error conditions
  - **Expected**: Clear error messages via st.error()
  - **Examples**:
    - "Ticker 'XYZ' not found"
    - "End date must be after start date"
    - "Portfolio weights must sum to 1.0 (currently {sum:.2f})"

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

The CI/CD pipeline is configured to run automatically on the following events:
- **Push to `stage` or `dev/*` branches**: Runs tests to validate changes before merge
- **Pull requests to `stage` or `main`**: Validates changes meet quality standards

**Branching workflow**:
- `dev/*` → `stage`: Development features tested before integration
- `stage` → `main`: Only after all tests pass on stage
- `main`: Production-ready code only

```yaml
name: Test Suite

on:
  push:
    branches: [ stage, dev/* ]
  pull_request:
    branches: [ stage, main ]

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
        pip install pytest pytest-cov pytest-mock pytest-asyncio responses faker
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov=streamlit_app --cov-report=xml --cov-report=html --cov-report=term
    
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
        pip install flake8 black isort
    
    - name: Run linters
      run: |
        flake8 src/ streamlit_app.py --max-line-length=120
        black --check src/ streamlit_app.py
        isort --check-only src/ streamlit_app.py

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit security scan
      run: |
        pip install bandit
        bandit -r src/ -ll
```

**Note**: `main.py` (FastAPI backend) is excluded from testing as it is deprecated.

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
