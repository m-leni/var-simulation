"""
This module provides functions for calculating various financial metrics,
including weighted moving averages and Value at Risk (VaR).
"""
import numpy as np
import pandas as pd
from scipy import stats

from typing import Union, Dict


def calculate_portfolio_returns(
    stock_prices: Dict[str, np.ndarray],
    weights: np.ndarray
) -> np.ndarray:
    """
    Calculate portfolio returns from individual stock prices and weights.
    
    Args:
        stock_prices (Dict[str, np.ndarray]): Dictionary mapping ticker symbols to price arrays
        weights (np.ndarray): Array of portfolio weights corresponding to the stocks
        
    Returns:
        np.ndarray: Array of portfolio returns
    """
    if len(stock_prices) != len(weights):
        raise ValueError("Number of stocks must match number of weights")
    
    # Calculate returns for each stock
    stock_returns = {
        ticker: calculate_returns(prices)
        for ticker, prices in stock_prices.items()
    }
    
    # Create a returns matrix
    returns_matrix = np.column_stack([
        returns for returns in stock_returns.values()
    ])
    
    # Calculate portfolio returns
    portfolio_returns = np.dot(returns_matrix, weights)
    
    return portfolio_returns


def portfolio_var(
    returns: np.ndarray,
    weights: np.ndarray,
    confidence_level: float = 0.95,
    investment_value: float = 100000.0,
    method: str = "historical"
) -> Dict[str, float]:
    """
    Calculate portfolio Value at Risk (VaR) using either historical or parametric method.
    
    Args:
        returns (np.ndarray): Matrix of asset returns (each column is an asset)
        weights (np.ndarray): Array of portfolio weights
        confidence_level (float): Confidence level for VaR calculation
        investment_value (float): Total portfolio value
        method (str): VaR calculation method ('historical' or 'parametric')
    
    Returns:
        Dict[str, float]: Dictionary containing VaR and other risk metrics
    """
    # Calculate portfolio returns
    portfolio_returns = np.dot(returns, weights)
    
    # Calculate VaR based on method
    if method == "historical":
        var = historical_var(portfolio_returns, confidence_level, investment_value)
    else:  # parametric
        var = parametric_var(portfolio_returns, confidence_level, investment_value)
    
    # Calculate additional risk metrics
    portfolio_std = np.std(portfolio_returns, ddof=1)
    portfolio_mean = np.mean(portfolio_returns)
    sharpe_ratio = (portfolio_mean / portfolio_std) * np.sqrt(252)  # Annualized
    
    return {
        "var": var,
        "daily_volatility": portfolio_std,
        "annualized_volatility": portfolio_std * np.sqrt(252),
        "expected_return": portfolio_mean,
        "annualized_return": portfolio_mean * 252,
        "sharpe_ratio": sharpe_ratio
    }


def calculate_returns(
    prices: Union[pd.Series, np.ndarray, list],
    method: str = 'log'
) -> pd.Series:
    """
    Calculate returns from a price series.
    
    Args:
        prices (Union[pd.Series, np.ndarray, list]): Series of asset prices
        method (str): Method to calculate returns - 'log' or 'simple'
    
    Returns:
        pd.Series: Series of returns
    """
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
    
    if method == 'log':
        returns = np.log(prices / prices.shift(1))
    elif method == 'simple':
        returns = (prices / prices.shift(1)) - 1
    else:
        raise ValueError("method must be either 'log' or 'simple'")
    
    return returns


def historical_var(
    returns: Union[pd.Series, np.ndarray, list],
    confidence_level: float = 0.95,
    investment_value: float = 1.0
) -> float:
    """
    Calculate historical Value at Risk (VaR) for a series of returns.
    
    Args:
        returns (Union[pd.Series, np.ndarray, list]): Series of asset/portfolio returns
        confidence_level (float): Confidence level for VaR calculation (default: 0.95)
        investment_value (float): Current value of the investment (default: 1.0)
    
    Returns:
        float: Value at Risk at the specified confidence level
    """
    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)
    
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1")
    
    # Calculate the percentile corresponding to the confidence level
    var_percentile = 1 - confidence_level
    var = np.percentile(returns, var_percentile * 100)
    
    # Convert to monetary value
    var_value = investment_value * abs(var)
    
    return float(var_value)


def parametric_var(
    returns: Union[pd.Series, np.ndarray, list],
    confidence_level: float = 0.95,
    investment_value: float = 1.0
) -> float:
    """
    Calculate parametric (Gaussian) Value at Risk (VaR).
    
    Args:
        returns (Union[pd.Series, np.ndarray, list]): Series of asset/portfolio returns
        confidence_level (float): Confidence level for VaR calculation (default: 0.95)
        investment_value (float): Current value of the investment (default: 1.0)
    
    Returns:
        float: Value at Risk at the specified confidence level
    """
    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)
    
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1")
    
    # Calculate mean and standard deviation of returns
    mu = returns.mean()
    sigma = returns.std()
    
    # Find the z-score for the confidence level
    z_score = stats.norm.ppf(1 - confidence_level)
    
    # Calculate VaR
    var = -(mu + z_score * sigma)
    var_value = investment_value * abs(var)
    
    return var_value


def calculate_cumulative_yield(
    prices: Union[pd.Series, pd.DataFrame],
    method: str = 'simple'
) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate the cumulative yield (return) relative to the start date.
    
    Args:
        prices (Union[pd.Series, pd.DataFrame]): Price series or DataFrame of prices.
            If DataFrame, calculates cumulative yield for each column.
        method (str): Method to calculate returns
            'simple': (current_price - start_price) / start_price * 100
            'log': (exp(sum(log_returns)) - 1) * 100
    
    Returns:
        Union[pd.Series, pd.DataFrame]: Cumulative yield in percentage terms
        
    Example:
        If stock starts at $100 and goes to $120, cumulative yield is 20%
        If it then goes to $150, cumulative yield is 50% (relative to start)
    """
    if not isinstance(prices, (pd.Series, pd.DataFrame)):
        prices = pd.Series(prices)
    
    if method not in ['simple', 'log']:
        raise ValueError("method must be either 'simple' or 'log'")
    
    if isinstance(prices, pd.Series):
        start_price = prices.iloc[0]
        if method == 'simple':
            cum_yield = ((prices - start_price) / start_price) * 100
        else:  # log returns
            returns = calculate_returns(prices, method='log')
            cum_yield = (np.exp(returns.cumsum()) - 1) * 100
            
    else:  # DataFrame
        cum_yield = pd.DataFrame(index=prices.index)
        for column in prices.columns:
            start_price = prices[column].iloc[0]
            if method == 'simple':
                cum_yield[column] = ((prices[column] - start_price) / start_price) * 100
            else:  # log returns
                returns = calculate_returns(prices[column], method='log')
                cum_yield[column] = (np.exp(returns.cumsum()) - 1) * 100
    
    return cum_yield


def historic_pe_ratio(
    prices: Union[pd.DataFrame, pd.Series],
    financials: pd.DataFrame,
    price_date_col: str = 'Date',
    price_close_col: str = 'Close',
    eps_col: str = 'Basic EPS',
    use_last_available: bool = True
) -> pd.Series:
    """
    Calculate historical Price-to-Earnings (P/E) ratio as close price divided by yearly EPS.

    Args:
        prices: DataFrame or Series containing closing prices. If DataFrame, must contain
            a date column specified by `price_date_col` or have a DatetimeIndex.
        financials: DataFrame containing EPS information. Expected either:
            - a 'Year' column and an EPS column; or
            - a 'Date' column with quarterly entries and an EPS column (will be grouped by year)
        price_date_col: Name of the date column in `prices` (default 'Date'). Ignored if `prices` has DatetimeIndex.
        price_close_col: Name of the close price column in `prices` (default 'Close').
        eps_candidates: Optional list of column names to try for EPS (defaults to common names).
        use_last_available: If True, for a price date use the latest EPS year that is <= the price year.

    Returns:
        pd.Series: P/E ratio indexed by the prices' dates.
    """

    # Minimal implementation: use last available annual EPS for each price date
    # Prepare price series
    if isinstance(prices, pd.Series):
        price_ser = prices.copy()
        price_ser.index = pd.to_datetime(price_ser.index)
        if price_ser.name is None:
            price_ser.name = 'Close'
    else:
        price_df = prices.copy()
        if price_date_col in price_df.columns:
            price_df[price_date_col] = pd.to_datetime(price_df[price_date_col])
            price_df = price_df.set_index(price_date_col)
        price_ser = price_df[price_close_col].copy()

    # Prepare yearly EPS
    fin = financials.copy()
    if 'Year' in fin.columns:
        yearly_eps = fin.set_index('Year')[eps_col].astype(float)
    else:
        fin['Date'] = pd.to_datetime(fin['Date'])
        fin['Year'] = fin['Date'].dt.year
        yearly_eps = fin.groupby('Year')[eps_col].sum()

    yearly_eps = yearly_eps.sort_index()

    # Build a reindexed series covering the range needed and forward-fill to use last available EPS
    min_year = int(min(yearly_eps.index.min(), price_ser.index.year.min()))
    max_year = int(max(yearly_eps.index.max(), price_ser.index.year.max()))
    reindexed = yearly_eps.reindex(range(min_year, max_year + 1)).ffill()

    # Map each price date to the EPS for that year (or last available prior year via ffill)
    years = price_ser.index.year
    eps_for_dates = reindexed.loc[years].values
    eps_series = pd.Series(eps_for_dates, index=price_ser.index)

    # Compute P/E (price / EPS) and replace infinities
    pe = price_ser / eps_series
    pe = pe.replace([np.inf, -np.inf], np.nan)
    pe.name = 'P/E'

    return pe


def forward_pe_ratio(
    current_price: Union[float, pd.Series],
    forward_eps: Union[float, pd.Series]
) -> Union[float, pd.Series]:
    """
    Calculate forward Price-to-Earnings (P/E) ratio using analyst EPS estimates.
    
    Forward P/E uses analyst estimates for future earnings rather than historical earnings,
    providing a forward-looking valuation metric.
    
    Args:
        current_price: Current stock price(s)
        forward_eps: Analyst consensus forward EPS estimate(s) for next 12 months or next fiscal year
    
    Returns:
        Union[float, pd.Series]: Forward P/E ratio(s). Returns np.nan for invalid values (zero or negative EPS).
    
    Example:
        >>> forward_pe_ratio(150.0, 6.0)
        25.0
        
        >>> prices = pd.Series([150, 160, 170])
        >>> eps = pd.Series([6.0, 6.5, 7.0])
        >>> forward_pe_ratio(prices, eps)
        0    25.000000
        1    24.615385
        2    24.285714
        dtype: float64
    """
    if isinstance(current_price, (pd.Series, pd.DataFrame)) or isinstance(forward_eps, (pd.Series, pd.DataFrame)):
        # Handle Series/DataFrame inputs
        pe = current_price / forward_eps
        pe = pe.replace([np.inf, -np.inf], np.nan)
        if isinstance(pe, pd.Series):
            pe.name = 'Forward P/E'
        return pe
    else:
        # Handle scalar inputs
        if forward_eps <= 0:
            return np.nan
        return current_price / forward_eps