"""
Example test demonstrating use of expected outputs for deterministic testing.

This module shows how to:
1. Load expected outputs from JSON files
2. Compare function results with expected values
3. Use appropriate tolerance levels for different function types
"""
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.metrics import (
    calculate_returns,
    historical_var,
    parametric_var,
)

# Path to expected outputs
EXPECTED_OUTPUTS_PATH = Path(__file__).parent / 'data' / 'outputs' / 'metrics_expected.json'


@pytest.fixture
def expected_outputs():
    """Load expected outputs from JSON file."""
    with open(EXPECTED_OUTPUTS_PATH, 'r') as f:
        return json.load(f)


class TestWithExpectedOutputs:
    """Example tests using expected outputs for deterministic validation."""
    
    def test_calculate_returns_log_method(self, expected_outputs):
        """Test log returns against expected deterministic output."""
        # Get test data
        test_case = expected_outputs['calculate_returns']['log_returns_sample']
        prices = pd.Series(test_case['input'])
        expected = test_case['expected']
        tolerance = test_case['tolerance']
        
        # Calculate returns
        result = calculate_returns(prices, method='log')
        actual = result.dropna().tolist()
        
        # Compare with expected (deterministic function, very tight tolerance)
        assert len(actual) == len(expected), "Result length mismatch"
        for i, (act, exp) in enumerate(zip(actual, expected)):
            assert abs(act - exp) < tolerance, \
                f"Mismatch at index {i}: {act} vs {exp}"
    
    def test_calculate_returns_simple_method(self, expected_outputs):
        """Test simple returns against expected deterministic output."""
        test_case = expected_outputs['calculate_returns']['simple_returns_sample']
        prices = pd.Series(test_case['input'])
        expected = test_case['expected']
        tolerance = test_case['tolerance']
        
        result = calculate_returns(prices, method='simple')
        actual = result.dropna().tolist()
        
        # Deterministic function - exact match expected
        assert len(actual) == len(expected)
        for act, exp in zip(actual, expected):
            assert abs(act - exp) < tolerance
    
    def test_historical_var_with_expected_output(self, expected_outputs):
        """Test historical VaR against expected output."""
        # Get sample returns from expected outputs
        sample_returns = np.array(
            expected_outputs['historical_var']['sample_returns']
        )
        
        # Test confidence level 95%
        test_case = expected_outputs['historical_var']['test_cases']['confidence_95_investment_10000']
        result = historical_var(
            sample_returns,
            confidence_level=test_case['confidence_level'],
            investment_value=test_case['investment_value']
        )
        
        expected = test_case['expected_var']
        tolerance = test_case['tolerance']
        
        # Historical VaR is deterministic for fixed input
        assert abs(result - expected) < tolerance, \
            f"VaR mismatch: {result} vs {expected}"
    
    def test_historical_var_scaling(self, expected_outputs):
        """Test that VaR scales linearly with investment value."""
        sample_returns = np.array(
            expected_outputs['historical_var']['sample_returns']
        )
        
        scaling_test = expected_outputs['historical_var']['test_cases']['scaling_test']
        
        var1 = historical_var(sample_returns, 0.95, 10000)
        var2 = historical_var(sample_returns, 0.95, 20000)
        
        # Check linear scaling
        ratio = var2 / var1
        expected_ratio = scaling_test['ratio']
        tolerance = scaling_test['tolerance']
        
        assert abs(ratio - expected_ratio) < tolerance, \
            f"VaR scaling not linear: ratio={ratio}, expected={expected_ratio}"
    
    def test_parametric_var_with_tolerance(self, expected_outputs):
        """Test parametric VaR with appropriate tolerance for statistical method."""
        sample_returns = np.array(
            expected_outputs['parametric_var']['sample_returns']
        )
        
        test_case = expected_outputs['parametric_var']['test_cases']['confidence_95_investment_10000']
        result = parametric_var(
            sample_returns,
            confidence_level=test_case['confidence_level'],
            investment_value=test_case['investment_value']
        )
        
        expected = test_case['expected_var_approx']
        tolerance = test_case['tolerance']
        
        # Parametric VaR uses statistical assumptions, needs wider tolerance
        assert abs(result - expected) < tolerance, \
            f"Parametric VaR outside tolerance: {result} vs {expected}±{tolerance}"


class TestToleranceLevels:
    """Demonstrate different tolerance levels for different function types."""
    
    def test_deterministic_function_tight_tolerance(self, expected_outputs):
        """Deterministic functions should match within floating-point precision."""
        # Use tolerance of 1e-10 for deterministic calculations
        test_case = expected_outputs['calculate_returns']['log_returns_sample']
        prices = pd.Series([100, 110, 105])
        
        result = calculate_returns(prices, method='log')
        expected = test_case['expected']
        
        # Very tight tolerance for deterministic function
        np.testing.assert_allclose(
            result.dropna().tolist(),
            expected,
            atol=1e-10,
            rtol=0
        )
    
    def test_statistical_function_relaxed_tolerance(self, expected_outputs):
        """Statistical functions need relative tolerance due to approximations."""
        sample_returns = np.array(
            expected_outputs['parametric_var']['sample_returns']
        )
        
        result = parametric_var(sample_returns, 0.95, 10000)
        expected = 193.0  # Approximate from parametric method
        
        # Relative tolerance of 5% for statistical approximation
        np.testing.assert_allclose(
            result,
            expected,
            rtol=0.05  # 5% relative tolerance
        )
    
    def test_portfolio_function_wide_tolerance(self, expected_outputs):
        """Portfolio calculations with correlations need wider tolerance."""
        # Portfolio VaR involves correlation matrices and can have more variation
        # Use tolerance of 10% for complex portfolio calculations
        tolerance_note = expected_outputs['portfolio_var']['test_cases']['historical_method_95']['note']
        assert "10%" in tolerance_note, "Portfolio tests should use 10% tolerance"


# Example of how to add new expected outputs when functions are updated
def generate_new_expected_outputs():
    """
    Helper function to regenerate expected outputs when functions are intentionally changed.
    
    This should be run manually after verifying the new function behavior is correct.
    Do not run automatically in tests!
    """
    prices = pd.Series([100, 110, 105])
    log_returns = calculate_returns(prices, method='log')
    simple_returns = calculate_returns(prices, method='simple')
    
    new_outputs = {
        'calculate_returns': {
            'log_returns_sample': {
                'input': prices.tolist(),
                'expected': log_returns.dropna().tolist(),
                'tolerance': 1e-10
            },
            'simple_returns_sample': {
                'input': prices.tolist(),
                'expected': simple_returns.dropna().tolist(),
                'tolerance': 1e-10
            }
        }
    }
    
    print("New expected outputs:")
    print(json.dumps(new_outputs, indent=2))
    print("\nReview these values and update metrics_expected.json if correct!")


if __name__ == '__main__':
    # Run this manually to generate new expected outputs
    generate_new_expected_outputs()
