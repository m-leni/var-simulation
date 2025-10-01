"""
This module provides functions to fetch stock data from Yahoo Finance API.
"""
import yfinance as yf
from datetime import datetime, timedelta, date
import pandas as pd
from typing import Optional, Union

from .metrics import calculate_cumulative_yield

def fetch_stock_data(
    ticker: str,
    days: int = 252,  # Default to ~1 trading year
    end_date: Optional[Union[str, datetime]] = None
) -> pd.DataFrame:
    """
    Fetch daily stock data for a given ticker from Yahoo Finance.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple)
        days (int): Number of trading days of historical data to fetch (default: 252)
        end_date (Optional[Union[str, datetime]]): End date for the data fetch. 
            Can be string 'YYYY-MM-DD' or datetime object. If None, uses current date.
    
    Returns:
        pd.DataFrame: DataFrame containing the stock data with columns:
            - Date
            - Open
            - High
            - Low
            - Close
            - Adj Close
            - Volume
    
    Raises:
        ValueError: If the ticker is invalid or if data cannot be fetched
    """
    # Create ticker object
    stock = yf.Ticker(ticker)
    
    # Set end date to today if not specified
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate start date based on number of days
    start_date = end_date - timedelta(days=days)
    
    # Fetch the data
    try:
        df = stock.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1d'
        )
        
        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
    except Exception as e:
        raise ValueError(f"Error fetching data for ticker {ticker}: {str(e)}")
    
    df = (df.reset_index()
        [['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends']]
    )
    df.insert(1, 'Ticker', ticker)
    df.Date = df.Date.dt.date

    df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()

    df['yield'] = calculate_cumulative_yield(df['Close'])

    return df

def get_stock_info(ticker: str) -> dict:
    """
    Get basic information about a stock.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple)
    
    Returns:
        dict: Dictionary containing basic stock information including:
            - longName: Full company name
            - sector: Company sector
            - industry: Company industry
            - marketCap: Market capitalization
            - currency: Trading currency
            And other available information from Yahoo Finance
    
    Raises:
        ValueError: If the ticker is invalid or if data cannot be fetched
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        raise ValueError(f"Error fetching info for ticker {ticker}: {str(e)}")
