"""
Shared pytest fixtures and configuration for test suite.
"""
import pytest
import pandas as pd
import numpy as np
import sqlite3 as sql
import json
from pathlib import Path

# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent / 'data'

def load_json_data(filename):
    """Load test data from JSON file."""
    filepath = TEST_DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

@pytest.fixture
def sample_prices():
    """Load real AAPL price data from JSON, fallback to generated data."""
    data = load_json_data('aapl_sample.json')
    if data:
        return pd.Series(data['close'])
    # Fallback to generated data
    return pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 110])

@pytest.fixture
def sample_returns():
    """Generate sample returns for testing."""
    return np.array([0.01, -0.02, 0.015, -0.01, 0.02, 0.0, -0.015, 0.01, 0.005, -0.01])

@pytest.fixture
def sample_stock_data():
    """Load real AAPL stock data from JSON, fallback to generated data."""
    data = load_json_data('aapl_sample.json')
    if data:
        return pd.DataFrame({
            'Date': pd.to_datetime(data['dates']),
            'Ticker': [data['ticker']] * len(data['dates']),
            'Open': data['open'],
            'High': data['high'],
            'Low': data['low'],
            'Close': data['close'],
            'Volume': data['volume'],
            'Dividends': data['dividends'],
            'ema50': [np.mean(data['close'])] * len(data['dates']),  # Simplified EMA
            'ema200': [np.mean(data['close'])] * len(data['dates']),
            'yield': [0] * len(data['dates'])
        })
    # Fallback to generated data
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Ticker': ['AAPL'] * 10,
        'Open': [100, 102, 101, 103, 105, 104, 106, 108, 107, 110],
        'High': [102, 104, 103, 105, 107, 106, 108, 110, 109, 112],
        'Low': [99, 101, 100, 102, 104, 103, 105, 107, 106, 109],
        'Close': [101, 103, 102, 104, 106, 105, 107, 109, 108, 111],
        'Volume': [1000000] * 10,
        'Dividends': [0] * 10,
        'ema50': [100.5] * 10,
        'ema200': [99.5] * 10,
        'yield': [0] * 10
    })

@pytest.fixture
def sample_financial_data():
    """Generate sample financial data DataFrame."""
    return pd.DataFrame({
        'Year': [2020, 2021, 2022, 2023],
        'Total Revenue': [100.0, 110.0, 120.0, 130.0],
        'Total Expenses': [60.0, 65.0, 70.0, 75.0],
        'Gross Profit': [40.0, 45.0, 50.0, 55.0],
        'EBITDA': [30.0, 35.0, 40.0, 45.0],
        'Free Cash Flow': [20.0, 25.0, 30.0, 35.0],
        'Common Stock Dividend Paid': [5.0, 5.5, 6.0, 6.5],
        'Basic EPS': [2.0, 2.5, 3.0, 3.5]
    })

@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    conn = sql.connect(':memory:')
    yield conn
    conn.close()

@pytest.fixture
def portfolio_data():
    """Load real portfolio data from JSON (GOOGL, META, MSFT), fallback to generated data."""
    data = load_json_data('portfolio_sample.json')
    if data:
        return {
            'tickers': data['tickers'],
            'weights': np.array(data['weights']),
            'prices': {
                ticker: np.array(data[ticker]['close'])
                for ticker in data['tickers']
            },
            'investment_value': data['investment_value'],
            'confidence_levels': data['confidence_levels']
        }
    # Fallback to generated data
    return {
        'tickers': ['AAPL', 'GOOGL', 'MSFT'],
        'weights': np.array([0.4, 0.3, 0.3]),
        'prices': {
            'AAPL': np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 110]),
            'GOOGL': np.array([150, 152, 151, 153, 155, 154, 156, 158, 157, 160]),
            'MSFT': np.array([200, 202, 201, 203, 205, 204, 206, 208, 207, 210])
        }
    }

@pytest.fixture
def mock_stock_info():
    """Mock stock info data."""
    return {
        'symbol': 'AAPL',
        'shortName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 3000000000000,
        'currentPrice': 150.0,
        'fiftyTwoWeekHigh': 180.0,
        'fiftyTwoWeekLow': 120.0
    }

@pytest.fixture
def confidence_levels():
    """Common confidence levels for testing."""
    return [0.90, 0.95, 0.99]

@pytest.fixture
def investment_values():
    """Common investment values for testing."""
    return [1.0, 10000.0, 100000.0, 1000000.0]
