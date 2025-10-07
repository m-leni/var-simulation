# Test Expected Outputs

This directory contains expected outputs from metrics functions for deterministic testing.

## Purpose

These JSON files provide expected outputs that tests can compare against to ensure:
1. **Correctness**: Functions produce expected results
2. **Regression Prevention**: Changes don't break existing behavior
3. **Determinism**: Functions produce consistent results

## Files

### `metrics_expected.json`

Contains expected outputs for all metrics functions in `src/metrics.py`:

- **calculate_returns**: Log and simple returns calculations
- **historical_var**: Historical Value at Risk at various confidence levels
- **parametric_var**: Parametric VaR assuming normal distribution
- **portfolio_var**: Portfolio VaR for multiple assets
- **weighted_moving_average**: WMA with various window sizes
- **exponential_weighted_moving_average**: EWMA with different alphas
- **calculate_cumulative_yield**: Cumulative returns in percentage

## Tolerance Levels

### Deterministic Functions (tolerance: 1e-10)
Functions that should produce exactly the same output given the same input:
- `calculate_returns` (log and simple methods)
- `weighted_moving_average` (with fixed weights)
- `exponential_weighted_moving_average` (with fixed alpha)
- `calculate_cumulative_yield`

### Stochastic/Statistical Functions (tolerance: 0.05-0.1)
Functions that may have minor variations due to:
- Numerical precision in statistical calculations
- Portfolio correlation complexity
- Percentile calculations

Tolerance is typically 5-10% relative error:
- `historical_var` (percentile-based)
- `parametric_var` (normal distribution assumption)
- `portfolio_var` (complex correlation matrix)

## Usage in Tests

```python
import json

# Load expected outputs
with open('tests/data/outputs/metrics_expected.json', 'r') as f:
    expected = json.load(f)

# Test with tolerance
def test_historical_var():
    result = historical_var(sample_returns, 0.95, 10000)
    expected_value = expected['historical_var']['test_cases']['confidence_95_investment_10000']['expected_var']
    tolerance = expected['historical_var']['test_cases']['confidence_95_investment_10000']['tolerance']
    
    assert abs(result - expected_value) < tolerance
```

## Updating Expected Outputs

When function implementations change (with good reason), update the expected outputs:

1. Review the change to ensure it's intentional and correct
2. Run the functions with test inputs to get new outputs
3. Update the JSON file with new expected values
4. Document the change in commit message
5. Ensure tolerance levels are appropriate

## Test Data Sources

Expected outputs are calculated using:
- **AAPL data**: `tests/data/aapl_sample.json` (10 days of real stock data)
- **Portfolio data**: `tests/data/portfolio_sample.json` (GOOGL, META, MSFT)
- **Sample returns**: Predefined array for consistent testing

## Notes

- All outputs are generated from deterministic inputs
- Floating-point precision may cause minor differences across systems
- Use appropriate tolerance levels for each function type
- Non-deterministic tests (e.g., with random data) should use relative tolerance
