"""
Tests for the TUI stock analysis application.
"""
import pytest
import pandas as pd
from datetime import date, timedelta
from tui_app import StockMetricsDisplay


def test_stock_metrics_display():
    """Test the StockMetricsDisplay widget."""
    # Create a sample dataframe
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    data = {
        'Date': dates,
        'Open': [150.0 + i for i in range(len(dates))],
        'High': [152.0 + i for i in range(len(dates))],
        'Low': [148.0 + i for i in range(len(dates))],
        'Close': [151.0 + i for i in range(len(dates))],
        'Volume': [1000000 + i * 10000 for i in range(len(dates))],
    }
    df = pd.DataFrame(data)
    
    # Create widget instance
    widget = StockMetricsDisplay()
    
    # Test update_metrics
    widget.update_metrics(df, "AAPL")
    
    # Widget should contain formatted text
    assert widget.renderable is not None
    
    # Test with empty dataframe
    empty_df = pd.DataFrame()
    widget.update_metrics(empty_df, "TEST")
    assert widget.renderable is not None


def test_tui_app_imports():
    """Test that all TUI components can be imported."""
    from tui_app import (
        StockAnalysisApp,
        StockMetricsDisplay,
    )
    
    # Check classes exist
    assert StockAnalysisApp is not None
    assert StockMetricsDisplay is not None


def test_sample_data_generation():
    """Test sample data generation for demo."""
    from demo_tui import generate_sample_stock_data
    
    # Generate sample data
    df = generate_sample_stock_data("AAPL", days=30)
    
    # Verify structure
    assert len(df) > 0
    assert 'Date' in df.columns
    assert 'Open' in df.columns
    assert 'High' in df.columns
    assert 'Low' in df.columns
    assert 'Close' in df.columns
    assert 'Volume' in df.columns
    assert 'Ticker' in df.columns
    assert 'yield' in df.columns
    
    # Verify data types
    assert df['Open'].dtype in ['float64', 'float32']
    assert df['Volume'].dtype in ['int64', 'int32']
    
    # Verify reasonable values
    assert df['High'].min() > 0
    assert df['Low'].min() > 0
    assert df['Volume'].min() > 0
    assert (df['High'] >= df['Low']).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
