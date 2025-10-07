"""
Unit tests for src/metrics.py module.
"""
import pytest
import numpy as np
import pandas as pd
from src.metrics import (
    calculate_returns,
    historical_var,
    parametric_var,
    portfolio_var,
    calculate_portfolio_returns,
    weighted_moving_average,
    exponential_weighted_moving_average,
    calculate_cumulative_yield
)


class TestCalculateReturns:
    """Tests for calculate_returns function."""
    
    def test_log_returns_with_series(self, sample_prices):
        """Test log returns calculation with pandas Series."""
        returns = calculate_returns(sample_prices, method='log')
        assert isinstance(returns, pd.Series)
        assert len(returns) == len(sample_prices)
        assert returns.isna().sum() == 1  # First value should be NaN
        
    def test_simple_returns_with_series(self, sample_prices):
        """Test simple returns calculation with pandas Series."""
        returns = calculate_returns(sample_prices, method='simple')
        assert isinstance(returns, pd.Series)
        assert len(returns) == len(sample_prices)
        assert returns.isna().sum() == 1
        
    def test_log_returns_calculation(self):
        """Test correctness of log returns calculation."""
        prices = pd.Series([100, 110, 105])
        returns = calculate_returns(prices, method='log')
        expected_return_1 = np.log(110/100)
        assert abs(returns.iloc[1] - expected_return_1) < 1e-10
        
    def test_simple_returns_calculation(self):
        """Test correctness of simple returns calculation."""
        prices = pd.Series([100, 110, 105])
        returns = calculate_returns(prices, method='simple')
        assert abs(returns.iloc[1] - 0.10) < 1e-10  # (110-100)/100
        assert abs(returns.iloc[2] - (-0.045454545)) < 1e-8  # (105-110)/110
        
    def test_with_numpy_array(self):
        """Test with numpy array input."""
        prices = np.array([100, 102, 101, 103])
        returns = calculate_returns(prices, method='log')
        assert isinstance(returns, pd.Series)
        
    def test_with_list(self):
        """Test with list input."""
        prices = [100, 102, 101, 103]
        returns = calculate_returns(prices, method='log')
        assert isinstance(returns, pd.Series)
        
    def test_invalid_method(self):
        """Test error handling for invalid method."""
        prices = pd.Series([100, 102, 101])
        with pytest.raises(ValueError, match="method must be either 'log' or 'simple'"):
            calculate_returns(prices, method='invalid')


class TestHistoricalVaR:
    """Tests for historical_var function."""
    
    def test_basic_calculation(self, sample_returns):
        """Test basic VaR calculation."""
        var = historical_var(sample_returns, confidence_level=0.95, investment_value=10000)
        assert isinstance(var, float)
        assert var >= 0  # VaR should be positive
        
    def test_different_confidence_levels(self, sample_returns, confidence_levels):
        """Test VaR increases with confidence level."""
        vars = [historical_var(sample_returns, cl, 10000) for cl in confidence_levels]
        # Higher confidence should give higher VaR
        assert vars[0] <= vars[1] <= vars[2]
        
    def test_investment_value_scaling(self, sample_returns):
        """Test VaR scales linearly with investment value."""
        var1 = historical_var(sample_returns, 0.95, 10000)
        var2 = historical_var(sample_returns, 0.95, 20000)
        assert abs(var2 / var1 - 2.0) < 0.01  # Should be approximately 2x
        
    def test_with_series_input(self):
        """Test with pandas Series input."""
        returns = pd.Series(np.random.normal(0, 0.01, 100))
        var = historical_var(returns, 0.95, 10000)
        assert isinstance(var, float)
        assert var > 0
        
    def test_with_negative_returns(self):
        """Test with predominantly negative returns."""
        returns = np.array([-0.05, -0.03, -0.02, -0.01, 0.01, 0.02])
        var = historical_var(returns, 0.95, 10000)
        assert var > 0
        
    def test_edge_case_all_positive_returns(self):
        """Test with all positive returns."""
        returns = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        var = historical_var(returns, 0.95, 10000)
        assert var >= 0  # Should still return non-negative VaR


class TestParametricVaR:
    """Tests for parametric_var function."""
    
    def test_basic_calculation(self, sample_returns):
        """Test basic parametric VaR calculation."""
        var = parametric_var(sample_returns, confidence_level=0.95, investment_value=10000)
        assert isinstance(var, float)
        assert var >= 0
        
    def test_different_confidence_levels(self, sample_returns, confidence_levels):
        """Test VaR increases with confidence level."""
        vars = [parametric_var(sample_returns, cl, 10000) for cl in confidence_levels]
        assert vars[0] < vars[1] < vars[2]
        
    def test_normal_distribution(self):
        """Test with known normal distribution."""
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, 1000)
        var = parametric_var(returns, 0.95, 10000)
        # For normal(0, 0.01) at 95% confidence, VaR should be ~1.645 * 0.01 * 10000
        expected_var = 1.645 * 0.01 * 10000
        assert abs(var - expected_var) / expected_var < 0.15  # Within 15%
        
    def test_investment_value_scaling(self, sample_returns):
        """Test VaR scales linearly with investment value."""
        var1 = parametric_var(sample_returns, 0.95, 10000)
        var2 = parametric_var(sample_returns, 0.95, 30000)
        assert abs(var2 / var1 - 3.0) < 0.01
        
    def test_comparison_with_historical(self):
        """Test parametric vs historical VaR for normal distribution."""
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, 1000)
        hist_var = historical_var(returns, 0.95, 10000)
        param_var = parametric_var(returns, 0.95, 10000)
        # They should be similar for normal distribution
        assert abs(hist_var - param_var) / hist_var < 0.2  # Within 20%


class TestPortfolioReturns:
    """Tests for calculate_portfolio_returns function."""
    
    def test_basic_calculation(self, portfolio_data):
        """Test basic portfolio returns calculation."""
        returns = calculate_portfolio_returns(
            portfolio_data['prices'], 
            portfolio_data['weights']
        )
        assert isinstance(returns, np.ndarray)
        assert len(returns) == len(portfolio_data['prices']['AAPL']) - 1
        
    def test_equal_weights(self):
        """Test with equal weights."""
        prices = {
            'A': np.array([100, 110, 120]),
            'B': np.array([50, 55, 60])
        }
        weights = np.array([0.5, 0.5])
        returns = calculate_portfolio_returns(prices, weights)
        assert len(returns) == 2
        
    def test_single_asset(self):
        """Test with single asset (weight = 1.0)."""
        prices = {'A': np.array([100, 110, 120])}
        weights = np.array([1.0])
        returns = calculate_portfolio_returns(prices, weights)
        # Should equal the asset's returns
        expected = np.log(np.array([110, 120]) / np.array([100, 110]))
        np.testing.assert_array_almost_equal(returns, expected)
        
    def test_mismatched_lengths_error(self):
        """Test error when number of stocks doesn't match weights."""
        prices = {'A': np.array([100, 110]), 'B': np.array([50, 55])}
        weights = np.array([1.0])  # Only 1 weight for 2 stocks
        with pytest.raises(ValueError, match="Number of stocks must match number of weights"):
            calculate_portfolio_returns(prices, weights)


class TestPortfolioVaR:
    """Tests for portfolio_var function."""
    
    def test_historical_method(self):
        """Test portfolio VaR with historical method."""
        returns = pd.DataFrame({
            'A': [0.01, -0.02, 0.015, -0.01, 0.02],
            'B': [0.015, -0.015, 0.02, -0.005, 0.01]
        })
        weights = np.array([0.6, 0.4])
        result = portfolio_var(returns, weights, 0.95, 10000, method='historical')
        assert isinstance(result, float)
        assert result >= 0
        
    def test_parametric_method(self):
        """Test portfolio VaR with parametric method."""
        returns = pd.DataFrame({
            'A': [0.01, -0.02, 0.015, -0.01, 0.02],
            'B': [0.015, -0.015, 0.02, -0.005, 0.01]
        })
        weights = np.array([0.6, 0.4])
        result = portfolio_var(returns, weights, 0.95, 10000, method='parametric')
        assert isinstance(result, float)
        assert result >= 0
        
    def test_invalid_method_error(self):
        """Test error for invalid method."""
        returns = pd.DataFrame({'A': [0.01, 0.02], 'B': [0.015, 0.01]})
        weights = np.array([0.5, 0.5])
        with pytest.raises(ValueError, match="method must be either 'historical' or 'parametric'"):
            portfolio_var(returns, weights, 0.95, 10000, method='invalid')


class TestWeightedMovingAverage:
    """Tests for weighted_moving_average function."""
    
    def test_basic_calculation(self, sample_prices):
        """Test basic WMA calculation."""
        wma = weighted_moving_average(sample_prices, window=3)
        assert isinstance(wma, pd.Series)
        assert len(wma) == len(sample_prices)
        
    def test_with_custom_weights(self, sample_prices):
        """Test with custom weights."""
        custom_weights = [0.5, 0.3, 0.2]
        wma = weighted_moving_average(sample_prices, window=3, weights=custom_weights)
        assert isinstance(wma, pd.Series)
        
    def test_window_size_validation(self, sample_prices):
        """Test error for invalid window size."""
        with pytest.raises(ValueError, match="Window size must be at least 1"):
            weighted_moving_average(sample_prices, window=0)
            
    def test_weights_length_mismatch(self, sample_prices):
        """Test error when weights length doesn't match window."""
        with pytest.raises(ValueError, match="Length of weights .* must match window size"):
            weighted_moving_average(sample_prices, window=3, weights=[0.5, 0.5])
            
    def test_with_numpy_array(self):
        """Test with numpy array input."""
        data = np.array([1, 2, 3, 4, 5])
        wma = weighted_moving_average(data, window=3)
        assert isinstance(wma, pd.Series)


class TestExponentialWeightedMovingAverage:
    """Tests for exponential_weighted_moving_average function."""
    
    def test_basic_calculation(self, sample_prices):
        """Test basic EWMA calculation."""
        ewma = exponential_weighted_moving_average(sample_prices, window=5)
        assert isinstance(ewma, pd.Series)
        assert len(ewma) == len(sample_prices)
        
    def test_with_custom_alpha(self, sample_prices):
        """Test with custom alpha."""
        ewma = exponential_weighted_moving_average(sample_prices, window=5, alpha=0.3)
        assert isinstance(ewma, pd.Series)
        
    def test_alpha_validation(self, sample_prices):
        """Test error for invalid alpha."""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            exponential_weighted_moving_average(sample_prices, window=5, alpha=1.5)
            
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            exponential_weighted_moving_average(sample_prices, window=5, alpha=0)
            
    def test_window_size_validation(self, sample_prices):
        """Test error for invalid window size."""
        with pytest.raises(ValueError, match="Window size must be at least 1"):
            exponential_weighted_moving_average(sample_prices, window=0)


class TestCalculateCumulativeYield:
    """Tests for calculate_cumulative_yield function."""
    
    def test_simple_yield_calculation(self):
        """Test simple cumulative yield calculation."""
        prices = pd.Series([100, 110, 120, 115])
        yields = calculate_cumulative_yield(prices, method='simple')
        assert isinstance(yields, pd.Series)
        assert abs(yields.iloc[0] - 0) < 1e-10  # First yield is 0
        assert abs(yields.iloc[1] - 10) < 1e-10  # 10% gain
        assert abs(yields.iloc[2] - 20) < 1e-10  # 20% gain
        assert abs(yields.iloc[3] - 15) < 1e-10  # 15% gain
        
    def test_log_yield_calculation(self):
        """Test log-based cumulative yield calculation."""
        prices = pd.Series([100, 110, 120])
        yields = calculate_cumulative_yield(prices, method='log')
        assert isinstance(yields, pd.Series)
        assert yields.iloc[0] == 0
        
    def test_with_dataframe(self):
        """Test with DataFrame input."""
        prices = pd.DataFrame({
            'A': [100, 110, 120],
            'B': [50, 55, 60]
        })
        yields = calculate_cumulative_yield(prices, method='simple')
        assert isinstance(yields, pd.DataFrame)
        assert yields.shape == prices.shape
        
    def test_invalid_method(self):
        """Test error for invalid method."""
        prices = pd.Series([100, 110, 120])
        with pytest.raises(ValueError, match="method must be either 'simple' or 'log'"):
            calculate_cumulative_yield(prices, method='invalid')
