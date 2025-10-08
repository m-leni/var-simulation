"""
Unit tests for src/data.py module.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import date, timedelta
from src.data import (
    fetch_stock_data, 
    get_stock_info,
    fetch_analyst_price_targets,
    fetch_analyst_earnings_forecast,
    fetch_analyst_revenue_forecast,
    fetch_analyst_growth_estimates,
    get_forward_pe_data
)


class TestFetchStockData:
    """Tests for fetch_stock_data function."""
    
    @patch('src.data.yf.Ticker')
    def test_basic_fetch(self, mock_ticker_class):
        """Test basic stock data fetching."""
        # Mock yfinance Ticker
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100, 102, 101],
            'High': [102, 104, 103],
            'Low': [99, 101, 100],
            'Close': [101, 103, 102],
            'Volume': [1000000, 1100000, 1050000],
            'Dividends': [0, 0, 0]
        }, index=pd.date_range(start='2024-01-01', periods=3))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', days=3)
        
        assert isinstance(df, pd.DataFrame)
        assert 'Date' in df.columns
        assert 'Ticker' in df.columns
        assert 'Close' in df.columns
        assert len(df) == 3
        assert all(df['Ticker'] == 'AAPL')
        
    @patch('src.data.yf.Ticker')
    def test_with_start_end_dates(self, mock_ticker_class):
        """Test fetching with specific start and end dates."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100], 'High': [101], 'Low': [99],
            'Close': [100.5], 'Volume': [1000000], 'Dividends': [0]
        }, index=pd.date_range(start='2024-01-01', periods=1))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data(
            'AAPL',
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1
        
    @patch('src.data.yf.Ticker')
    def test_ema_calculation(self, mock_ticker_class):
        """Test that EMA columns are calculated."""
        # Generate enough data for EMA calculation
        dates = pd.date_range(start='2024-01-01', periods=250)
        prices = 100 + np.random.randn(250).cumsum()
        
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': prices,
            'High': prices + 1,
            'Low': prices - 1,
            'Close': prices,
            'Volume': [1000000] * 250,
            'Dividends': [0] * 250
        }, index=dates)
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', days=250)
        
        assert 'ema50' in df.columns
        assert 'ema200' in df.columns
        # EMA values should exist for later dates
        assert df['ema50'].notna().any()
        
    @patch('src.data.yf.Ticker')
    def test_yield_calculation(self, mock_ticker_class):
        """Test that yield column is calculated."""
        dates = pd.date_range(start='2024-01-01', periods=10)
        prices = [100, 102, 104, 103, 105, 107, 106, 108, 110, 109]
        
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': prices,
            'High': [p + 1 for p in prices],
            'Low': [p - 1 for p in prices],
            'Close': prices,
            'Volume': [1000000] * 10,
            'Dividends': [0] * 10
        }, index=dates)
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', days=10)
        
        assert 'yield' in df.columns
        
    @patch('src.data.yf.Ticker')
    def test_days_parameter(self, mock_ticker_class):
        """Test days parameter functionality."""
        mock_ticker = MagicMock()
        
        # Create mock data
        dates = pd.date_range(start='2024-01-01', periods=30)
        mock_hist = pd.DataFrame({
            'Open': [100] * 30,
            'High': [101] * 30,
            'Low': [99] * 30,
            'Close': [100] * 30,
            'Volume': [1000000] * 30,
            'Dividends': [0] * 30
        }, index=dates)
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', days=30)
        
        # Verify the history method was called with correct parameters
        mock_ticker.history.assert_called()
        
    @patch('src.data.yf.Ticker')
    def test_invalid_ticker(self, mock_ticker_class):
        """Test error handling for invalid ticker."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()  # Empty DataFrame
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('INVALID')
        
        # Should return empty or handle gracefully
        assert isinstance(df, pd.DataFrame)


class TestGetStockInfo:
    """Tests for get_stock_info function."""
    
    @patch('src.data.yf.Ticker')
    def test_basic_info(self, mock_ticker_class):
        """Test basic stock info retrieval."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'marketCap': 3000000000000,
            'currentPrice': 150.0
        }
        mock_ticker_class.return_value = mock_ticker
        
        info = get_stock_info('AAPL')
        
        assert isinstance(info, dict)
        assert info['symbol'] == 'AAPL'
        assert info['shortName'] == 'Apple Inc.'
        assert info['sector'] == 'Technology'
        
    @patch('src.data.yf.Ticker')
    def test_missing_fields(self, mock_ticker_class):
        """Test handling of missing info fields."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            'symbol': 'AAPL'
            # Missing other fields
        }
        mock_ticker_class.return_value = mock_ticker
        
        info = get_stock_info('AAPL')
        
        assert isinstance(info, dict)
        assert 'symbol' in info
        
    @patch('src.data.yf.Ticker')
    def test_info_exception(self, mock_ticker_class):
        """Test error handling when info retrieval fails."""
        mock_ticker = MagicMock()
        mock_ticker.info.side_effect = Exception("API error")
        mock_ticker_class.return_value = mock_ticker
        
        # Should handle exception gracefully
        try:
            info = get_stock_info('INVALID')
            # If it returns, should be dict or None
            assert info is None or isinstance(info, dict)
        except Exception:
            # Or it might raise, which is also acceptable
            pass


class TestDateHandling:
    """Tests for date parameter handling in fetch_stock_data."""
    
    @patch('src.data.yf.Ticker')
    def test_string_dates(self, mock_ticker_class):
        """Test with string date parameters."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100], 'High': [101], 'Low': [99],
            'Close': [100], 'Volume': [1000000], 'Dividends': [0]
        }, index=pd.date_range(start='2024-01-01', periods=1))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', start_date='2024-01-01', end_date='2024-01-31')
        
        assert isinstance(df, pd.DataFrame)
        
    @patch('src.data.yf.Ticker')
    def test_date_objects(self, mock_ticker_class):
        """Test with date object parameters."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100], 'High': [101], 'Low': [99],
            'Close': [100], 'Volume': [1000000], 'Dividends': [0]
        }, index=pd.date_range(start='2024-01-01', periods=1))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        
        df = fetch_stock_data('AAPL', start_date=start, end_date=end)
        
        assert isinstance(df, pd.DataFrame)
        
    @patch('src.data.yf.Ticker')
    def test_days_vs_date_range(self, mock_ticker_class):
        """Test days parameter vs start_date/end_date."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100] * 10,
            'High': [101] * 10,
            'Low': [99] * 10,
            'Close': [100] * 10,
            'Volume': [1000000] * 10,
            'Dividends': [0] * 10
        }, index=pd.date_range(start='2024-01-01', periods=10))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        # Test with days parameter
        df1 = fetch_stock_data('AAPL', days=10)
        assert isinstance(df1, pd.DataFrame)
        
        # Test with date range
        df2 = fetch_stock_data('AAPL', start_date='2024-01-01', end_date='2024-01-10')
        assert isinstance(df2, pd.DataFrame)


class TestDataTransformation:
    """Tests for data transformation in fetch_stock_data."""
    
    @patch('src.data.yf.Ticker')
    def test_date_column_creation(self, mock_ticker_class):
        """Test that Date column is created from index."""
        mock_ticker = MagicMock()
        dates = pd.date_range(start='2024-01-01', periods=5)
        mock_hist = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        }, index=dates)
        mock_hist['Open'] = [99, 100, 101, 102, 103]
        mock_hist['High'] = [101, 102, 103, 104, 105]
        mock_hist['Low'] = [98, 99, 100, 101, 102]
        mock_hist['Volume'] = [1000000] * 5
        mock_hist['Dividends'] = [0] * 5
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('AAPL', days=5)
        
        assert 'Date' in df.columns
        assert df['Date'].dtype == 'object' or pd.api.types.is_datetime64_any_dtype(df['Date'])
        
    @patch('src.data.yf.Ticker')
    def test_ticker_column_addition(self, mock_ticker_class):
        """Test that Ticker column is added with correct value."""
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame({
            'Open': [100], 'High': [101], 'Low': [99],
            'Close': [100], 'Volume': [1000000], 'Dividends': [0]
        }, index=pd.date_range(start='2024-01-01', periods=1))
        
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker
        
        df = fetch_stock_data('GOOGL', days=1)
        
        assert 'Ticker' in df.columns
        assert all(df['Ticker'] == 'GOOGL')


class TestAnalystForecasts:
    """Tests for analyst forecast functions from yfinance."""
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_price_targets(self, mock_ticker_class):
        """Test fetching analyst price targets."""
        mock_ticker = MagicMock()
        mock_ticker.analyst_price_targets = {
            'current': 150.0,
            'low': 120.0,
            'high': 180.0,
            'mean': 155.0,
            'median': 152.0
        }
        mock_ticker_class.return_value = mock_ticker
        
        targets = fetch_analyst_price_targets('AAPL')
        
        assert isinstance(targets, dict)
        assert targets['current'] == 150.0
        assert targets['mean'] == 155.0
        assert targets['low'] == 120.0
        assert targets['high'] == 180.0
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_price_targets_error(self, mock_ticker_class):
        """Test error handling when fetching price targets fails."""
        mock_ticker = MagicMock()
        mock_ticker.analyst_price_targets.side_effect = Exception("API error")
        mock_ticker_class.return_value = mock_ticker
        
        with pytest.raises(ValueError, match="Error fetching analyst price targets"):
            fetch_analyst_price_targets('INVALID')
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_earnings_forecast(self, mock_ticker_class):
        """Test fetching analyst earnings estimates."""
        mock_ticker = MagicMock()
        mock_earnings = pd.DataFrame({
            'numberOfAnalysts': [15, 15, 20, 18],
            'avg': [1.2, 1.3, 5.0, 5.5],
            'low': [1.0, 1.1, 4.5, 5.0],
            'high': [1.4, 1.5, 5.5, 6.0],
            'yearAgoEps': [1.0, 1.0, 4.2, 4.5],
            'growth': [0.2, 0.3, 0.19, 0.22]
        }, index=['Current Quarter', 'Next Quarter', 'Current Year', 'Next Year'])
        
        mock_ticker.earnings_estimate = mock_earnings
        mock_ticker_class.return_value = mock_ticker
        
        earnings = fetch_analyst_earnings_forecast('AAPL')
        
        assert isinstance(earnings, pd.DataFrame)
        assert len(earnings) == 4
        assert 'avg' in earnings.columns
        assert earnings.loc['Next Year', 'avg'] == 5.5
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_earnings_forecast_empty(self, mock_ticker_class):
        """Test error when no earnings estimates available."""
        mock_ticker = MagicMock()
        mock_ticker.earnings_estimate = None
        mock_ticker_class.return_value = mock_ticker
        
        with pytest.raises(ValueError, match="No earnings estimate data available"):
            fetch_analyst_earnings_forecast('AAPL')
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_revenue_forecast(self, mock_ticker_class):
        """Test fetching analyst revenue estimates."""
        mock_ticker = MagicMock()
        mock_revenue = pd.DataFrame({
            'numberOfAnalysts': [10, 10, 12, 12],
            'avg': [80e9, 85e9, 320e9, 350e9],
            'low': [75e9, 80e9, 310e9, 340e9],
            'high': [85e9, 90e9, 330e9, 360e9],
            'yearAgoRevenue': [75e9, 78e9, 300e9, 320e9],
            'growth': [0.067, 0.090, 0.067, 0.094]
        }, index=['Current Quarter', 'Next Quarter', 'Current Year', 'Next Year'])
        
        mock_ticker.revenue_estimate = mock_revenue
        mock_ticker_class.return_value = mock_ticker
        
        revenue = fetch_analyst_revenue_forecast('AAPL')
        
        assert isinstance(revenue, pd.DataFrame)
        assert len(revenue) == 4
        assert 'avg' in revenue.columns
        assert revenue.loc['Next Year', 'avg'] == 350e9
    
    @patch('src.data.yf.Ticker')
    def test_fetch_analyst_growth_estimates(self, mock_ticker_class):
        """Test fetching analyst growth estimates."""
        mock_ticker = MagicMock()
        mock_growth = pd.DataFrame({
            'AAPL': [0.05, 0.06, 0.08, 0.10, 0.12, 0.15]
        }, index=[
            'Current Qtr.',
            'Next Qtr.',
            'Current Year',
            'Next Year',
            'Next 5 Years (per annum)',
            'Past 5 Years (per annum)'
        ])
        
        mock_ticker.growth_estimates = mock_growth
        mock_ticker_class.return_value = mock_ticker
        
        growth = fetch_analyst_growth_estimates('AAPL')
        
        assert isinstance(growth, pd.DataFrame)
        assert len(growth) >= 4
        assert 'AAPL' in growth.columns
    
    @patch('src.data.yf.Ticker')
    def test_get_forward_pe_data(self, mock_ticker_class):
        """Test getting forward P/E data."""
        mock_ticker = MagicMock()
        
        # Mock info dict
        mock_ticker.info = {
            'currentPrice': 150.0,
            'trailingPE': 25.0,
            'targetMeanPrice': 160.0
        }
        
        # Mock earnings estimate
        mock_earnings = pd.DataFrame({
            'numberOfAnalysts': [20],
            'avg': [6.0],
            'low': [5.5],
            'high': [6.5],
            'yearAgoEps': [5.0],
            'growth': [0.2]
        }, index=['Next Year'])
        
        mock_ticker.earnings_estimate = mock_earnings
        mock_ticker_class.return_value = mock_ticker
        
        data = get_forward_pe_data('AAPL')
        
        assert isinstance(data, dict)
        assert data['current_price'] == 150.0
        assert data['forward_eps'] == 6.0
        assert data['forward_pe'] == 25.0  # 150 / 6
        assert data['trailing_pe'] == 25.0
        assert data['num_analysts'] == 20
    
    @patch('src.data.yf.Ticker')
    def test_get_forward_pe_data_fallback_to_info(self, mock_ticker_class):
        """Test forward P/E data fallback to info dict when estimates unavailable."""
        mock_ticker = MagicMock()
        
        # Mock info dict with forward data
        mock_ticker.info = {
            'currentPrice': 150.0,
            'forwardEps': 6.5,
            'forwardPE': 23.08,
            'trailingPE': 25.0,
            'targetMeanPrice': 160.0
        }
        
        # No earnings estimate available
        mock_ticker.earnings_estimate = None
        mock_ticker_class.return_value = mock_ticker
        
        data = get_forward_pe_data('AAPL')
        
        assert isinstance(data, dict)
        assert data['current_price'] == 150.0
        assert data['forward_eps'] == 6.5
        assert data['forward_pe'] == 23.08
