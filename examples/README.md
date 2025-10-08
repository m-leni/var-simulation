# Examples

This directory contains example scripts demonstrating how to use the var-simulation library.

## Analyst Forecast Example

The `analyst_forecast_example.py` script demonstrates how to use the new analyst forecast functions from yfinance:

### Features Demonstrated

1. **Fetch Analyst Price Targets**: Get analyst price target forecasts (low, high, mean, median)
2. **Fetch Earnings Forecasts**: Get analyst EPS estimates for current/next quarters and years
3. **Fetch Revenue Forecasts**: Get analyst revenue estimates
4. **Fetch Growth Estimates**: Get analyst growth projections
5. **Get Forward P/E Data**: Comprehensive function to get all forward P/E related data
6. **Calculate Forward P/E Ratio**: Manual calculation of forward P/E using custom values

### Running the Example

```bash
python examples/analyst_forecast_example.py
```

### Example Output

```
Analyst Forecast Data for AAPL
==================================================

1. Analyst Price Targets:
   Current Price: $150.00
   Target Mean:   $155.00
   Target Low:    $120.00
   Target High:   $180.00
   Target Median: $152.00

2. Analyst Earnings (EPS) Forecast:
                     numberOfAnalysts   avg   low  high  yearAgoEps  growth
Current Quarter                    15  1.20  1.00  1.40        1.00    0.20
Next Quarter                       15  1.30  1.10  1.50        1.00    0.30
Current Year                       20  5.00  4.50  5.50        4.20    0.19
Next Year                          18  5.50  5.00  6.00        4.50    0.22

...
```

## Available Functions

### Data Functions (`src.data`)

- `fetch_analyst_price_targets(ticker)` - Get analyst price targets
- `fetch_analyst_earnings_forecast(ticker)` - Get EPS estimates
- `fetch_analyst_revenue_forecast(ticker)` - Get revenue estimates
- `fetch_analyst_growth_estimates(ticker)` - Get growth projections
- `get_forward_pe_data(ticker)` - Get comprehensive forward P/E data

### Metrics Functions (`src.metrics`)

- `forward_pe_ratio(current_price, forward_eps)` - Calculate forward P/E ratio

## Use Cases

### 1. Valuation Analysis
Compare current stock price with analyst targets to identify potential opportunities.

### 2. Forward P/E Calculation
Use analyst estimates to calculate forward-looking P/E ratios for better valuation.

### 3. Growth Analysis
Analyze analyst growth estimates to understand future expectations.

### 4. Earnings Tracking
Monitor analyst EPS estimates and revisions over time.
