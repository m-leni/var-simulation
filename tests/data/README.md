# Test Data

This directory contains real stock market data samples used for testing.

## Files

### `aapl_sample.json`
Real AAPL (Apple Inc.) stock data for the last 10 trading days.

**Structure:**
- `ticker`: Stock ticker symbol
- `description`: Brief description
- `dates`: Trading dates (YYYY-MM-DD)
- `open`: Opening prices
- `high`: Daily high prices
- `low`: Daily low prices
- `close`: Closing prices
- `volume`: Trading volumes
- `dividends`: Dividend payments

**Usage:**
Tests use this data via the `sample_stock_data` and `sample_prices` fixtures in `conftest.py`.

### `portfolio_sample.json`
Portfolio data for GOOGL, META, and MSFT with equal weights.

**Structure:**
- `tickers`: List of stock symbols ["GOOGL", "META", "MSFT"]
- `weights`: Portfolio weights [0.33, 0.33, 0.34]
- `investment_value`: Total portfolio value (10000)
- `confidence_levels`: VaR confidence levels [0.90, 0.95, 0.99]
- `dates`: Trading dates
- `[TICKER]`: Price data for each stock
  - `open`, `high`, `low`, `close`, `volume`, `dividends`

**Usage:**
Tests use this data via the `portfolio_data` fixture in `conftest.py`.

## Data Source

This data represents realistic market data for testing purposes. The fixtures in `conftest.py` automatically load this data when available, falling back to generated data if files are missing.

## Updating Data

To update the test data with more recent values, edit the JSON files directly or fetch new data and save it in the same format. The test suite will automatically use the updated data.
