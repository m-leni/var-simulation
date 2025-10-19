"""
This module provides functions for calculating trading strategies and generating signals.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional


def calculate_buy_and_hold_returns(
    prices: pd.Series,
    initial_capital: float = 10000.0
) -> pd.Series:
    """
    Calculate returns for a buy and hold strategy.
    
    Args:
        prices: Series of closing prices
        initial_capital: Initial investment amount
        
    Returns:
        Series of portfolio values over time
    """
    if len(prices) == 0:
        return pd.Series(dtype=float)
    
    # Calculate number of shares bought at first price
    first_price = prices.iloc[0]
    shares = initial_capital / first_price
    
    # Portfolio value = shares * current price
    portfolio_value = shares * prices
    
    return portfolio_value


def calculate_ema_crossover_signals(
    df: pd.DataFrame,
    short_window: int = 50,
    long_window: int = 200
) -> pd.DataFrame:
    """
    Generate BUY/SELL signals based on EMA crossover strategy.
    
    Buy when short EMA crosses above long EMA (golden cross)
    Sell when short EMA crosses below long EMA (death cross)
    
    Args:
        df: DataFrame with 'Close', 'ema50', 'ema200' columns
        short_window: Short EMA period (default 50)
        long_window: Long EMA period (default 200)
        
    Returns:
        DataFrame with added 'signal' column
    """
    df = df.copy()
    
    # Initialize signal column
    df['signal'] = 'HOLD'
    
    # Ensure we have the EMAs
    if 'ema50' not in df.columns or 'ema200' not in df.columns:
        return df
    
    # Calculate crossovers
    # Buy signal: EMA50 crosses above EMA200
    # Sell signal: EMA50 crosses below EMA200
    for i in range(1, len(df)):
        prev_short = df.iloc[i-1]['ema50']
        prev_long = df.iloc[i-1]['ema200']
        curr_short = df.iloc[i]['ema50']
        curr_long = df.iloc[i]['ema200']
        
        # Check for valid values
        if pd.isna(prev_short) or pd.isna(prev_long) or pd.isna(curr_short) or pd.isna(curr_long):
            continue
            
        # Golden cross - BUY signal
        if prev_short <= prev_long and curr_short > curr_long:
            df.iloc[i, df.columns.get_loc('signal')] = 'BUY'
        # Death cross - SELL signal
        elif prev_short >= prev_long and curr_short < curr_long:
            df.iloc[i, df.columns.get_loc('signal')] = 'SELL'
    
    return df


def calculate_strategy_returns(
    df: pd.DataFrame,
    signals: pd.DataFrame,
    initial_capital: float = 10000.0
) -> pd.Series:
    """
    Calculate returns for a trading strategy based on BUY/SELL signals.
    
    Args:
        df: DataFrame with 'Date' and 'Close' columns
        signals: DataFrame with 'Date' and 'signal' columns
        initial_capital: Initial investment amount
        
    Returns:
        Series of portfolio values over time indexed by date
    """
    # Merge price data with signals
    df_merged = df[['Date', 'Close']].merge(
        signals[['Date', 'signal']], 
        on='Date', 
        how='left'
    )
    df_merged['signal'] = df_merged['signal'].fillna('HOLD')
    
    # Initialize tracking variables
    cash = initial_capital
    shares = 0
    portfolio_values = []
    
    for _, row in df_merged.iterrows():
        price = row['Close']
        signal = row['signal']
        
        # Execute trades
        if signal == 'BUY' and cash > 0:
            # Buy as many shares as possible
            shares = cash / price
            cash = 0
        elif signal == 'SELL' and shares > 0:
            # Sell all shares
            cash = shares * price
            shares = 0
        
        # Calculate portfolio value
        portfolio_value = cash + (shares * price)
        portfolio_values.append(portfolio_value)
    
    return pd.Series(portfolio_values, index=df_merged['Date'])


def initialize_default_strategies(conn) -> None:
    """
    Initialize default trading strategies in the database.
    
    Args:
        conn: Database connection
    """
    from src.database import insert_strategy
    import json
    
    # Buy and Hold S&P 500
    insert_strategy(
        name="Buy and Hold S&P 500",
        description="Simple buy and hold strategy on S&P 500 index (^GSPC)",
        strategy_type="buy_and_hold",
        parameters=json.dumps({"ticker": "^GSPC"}),
        conn=conn
    )
    
    # EMA Crossover Strategy
    insert_strategy(
        name="EMA 50/200 Crossover",
        description="Golden cross (50 EMA crosses above 200 EMA) generates BUY, death cross generates SELL",
        strategy_type="ema_crossover",
        parameters=json.dumps({"short_window": 50, "long_window": 200}),
        conn=conn
    )
    
    # Buy and Hold SPY
    insert_strategy(
        name="Buy and Hold SPY",
        description="Simple buy and hold strategy on SPY ETF",
        strategy_type="buy_and_hold",
        parameters=json.dumps({"ticker": "SPY"}),
        conn=conn
    )
