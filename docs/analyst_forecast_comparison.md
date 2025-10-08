# Analyst Forecast Data: yfinance vs FMP API

## Comparison

This document explains the difference between the two approaches for fetching analyst forecast data.

### yfinance-based Functions (Recommended)

**Functions:**
- `fetch_analyst_price_targets(ticker)`
- `fetch_analyst_earnings_forecast(ticker)`
- `fetch_analyst_revenue_forecast(ticker)`
- `fetch_analyst_growth_estimates(ticker)`
- `get_forward_pe_data(ticker)`

**Advantages:**
- ✅ **No API key required** - Free and easy to use
- ✅ **No rate limits** - No usage restrictions
- ✅ **Reliable data source** - Yahoo Finance is widely used
- ✅ **Forward P/E support** - Direct access to forward P/E ratios
- ✅ **Comprehensive data** - Price targets, EPS, revenue, growth estimates

**Data Available:**
- Analyst price targets (current, low, high, mean, median)
- EPS estimates (current quarter, next quarter, current year, next year)
- Revenue estimates (same periods as EPS)
- Growth rate estimates (quarterly, yearly, 5-year)
- Number of analysts providing estimates
- Forward and trailing P/E ratios

**Example Usage:**
```python
from src.data import get_forward_pe_data

# Get comprehensive forward P/E data
data = get_forward_pe_data('AAPL')
print(f"Forward P/E: {data['forward_pe']}")
print(f"Target Price: {data['target_price']}")
print(f"Forward EPS: {data['forward_eps']}")
```

### FMP API-based Function (Legacy)

**Function:**
- `fetch_financial_forecast(ticker, api_key)`

**Advantages:**
- More detailed quarterly breakdowns
- Historical estimate revisions
- Additional fundamental metrics

**Disadvantages:**
- ❌ **Requires API key** - Must sign up and get key
- ❌ **Rate limited** - Free tier has usage limits
- ❌ **Potential costs** - May require paid plan for full access
- ❌ **Additional setup** - Need to manage API keys

**When to Use:**
- When you need historical estimate revisions
- When you already have an FMP API subscription
- When you need very specific fundamental metrics not available in yfinance

## Recommendation

For P/E ratio calculations and general analyst forecast needs, **use the yfinance-based functions** as they provide:
1. Easier setup (no API key)
2. No usage limits
3. All data needed for forward P/E calculations
4. Better integration with other yfinance data

The FMP API should only be used if you specifically need features not available in yfinance.

## Migration from FMP to yfinance

If you're currently using `fetch_financial_forecast` with FMP API:

```python
# Old approach (requires API key)
from src.data import fetch_financial_forecast
forecast = fetch_financial_forecast('AAPL', api_key='your_key')

# New approach (no API key needed)
from src.data import fetch_analyst_earnings_forecast, fetch_analyst_revenue_forecast
earnings = fetch_analyst_earnings_forecast('AAPL')
revenue = fetch_analyst_revenue_forecast('AAPL')
```

For forward P/E calculations:

```python
# New comprehensive approach
from src.data import get_forward_pe_data

pe_data = get_forward_pe_data('AAPL')
# Returns: current_price, forward_eps, forward_pe, trailing_pe, target_price, num_analysts
```
