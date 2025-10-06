"""
This module provides functions to fetch stock data from Yahoo Finance API.
"""
import os
import ssl
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import requests
import yfinance as yf

from .metrics import calculate_cumulative_yield

from typing import Optional, Union, Dict

def scrape_qqq_holdings() -> pd.DataFrame:
    """
    Scrape QQQ holdings table from companiesmarketcap.com.
    
    Returns:
        pd.DataFrame: DataFrame containing QQQ holdings with columns:
            - Weight: Percentage weight in the index
            - Company Name: Name of the company
            - Ticker: Stock ticker symbol
            - Coupon Rate: Coupon rate if applicable
            - Shares Held: Number of shares held
    """
    url = "https://companiesmarketcap.com/invesco-qqq-trust/holdings/"
    
    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    # Create SSL context that doesn't verify certificates
    context = ssl._create_unverified_context()
    
    # Make the request
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table
    table = soup.find('div', {'class': 'table-container'})
    
    if not table:
        raise ValueError("Could not find holdings table on the page")
    
    # Extract data
    rows = []
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 5:  # Ensure row has all expected columns
            weight = cols[0].text.strip().rstrip('%')
            company = cols[1].text.strip()
            ticker = cols[2].text.strip()
            coupon = cols[3].text.strip()
            shares = cols[4].text.strip().replace(',', '')
            
            rows.append({
                'Weight': float(weight) / 100 if weight else None,
                'Company Name': company,
                'Ticker': ticker,
                'Coupon Rate': float(coupon.rstrip('%'))/100 if coupon and coupon != '-' else None,
                'Shares Held': int(shares) if shares and shares != '-' else None
            })
    
    # Create DataFrame
    df = pd.DataFrame(rows).drop(columns=['Coupon Rate', 'Shares Held']).reindex(['Ticker', 'Company Name', 'Weight'], axis=1)

    df.to_sql('qqq_holdings_live', if_exists='replace', index=False, con='sqlite:///database.db')
    
    return df
    
def fetch_financial_data(
    ticker: str,
) -> pd.DataFrame:
    """
    Fetch historical profit and loss data for a given ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple)
        start_date (Optional[Union[str, datetime, date]]): Start date for data fetch.
            Defaults to 5 years ago.
        end_date (Optional[Union[str, datetime, date]]): End date for data fetch.
            Defaults to current date.
    
    Returns:
        pd.DataFrame: DataFrame containing financial data with columns:
            - Date (index)
            - Revenue
            - GrossProfit
            - OperatingIncome
            - NetIncome
            - EPS
    """
    # Create ticker object
    stock = yf.Ticker(ticker)
    
    try:
        # Fetch yearly financials
        df = pd.concat([stock.financials, stock.cashflow], axis=0)

        # Rows to keep for fundamental analysis
        df = df.T[[
            'Total Revenue', 
            'Total Expenses',
            'Gross Profit', 
            'EBITDA', 
            'Free Cash Flow',
            'Common Stock Dividend Paid',
            'Basic EPS'
        ]].T

        # Convert to millions
        for col in df.columns:
            if col != 'Basic EPS':
                df[col] = df[col]/1e9
        
        if df.empty:
            raise ValueError(f"No financial data found for ticker {ticker}")        
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error fetching financial data for {ticker}: {str(e)}")


def fetch_financial_forecast(
    ticker: str,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch analyst forecasts for profit and loss data.
    Uses Financial Modeling Prep API (requires API key).
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple)
        api_key (Optional[str]): FMP API key. If not provided, will look for FMP_API_KEY env variable.
    
    Returns:
        pd.DataFrame: DataFrame containing forecast data with same columns as fetch_financial_data:
            - Revenue
            - GrossProfit
            - OperatingIncome
            - NetIncome
            - EPS
    """
    # Get API key
    api_key = api_key or os.getenv('FMP_API_KEY')
    if not api_key:
        raise ValueError("FMP API key not provided. Set FMP_API_KEY environment variable or pass api_key parameter.")
    
    base_url = "https://financialmodelingprep.com/stable"
    
    try:
        # Fetch analyst estimates
        response = requests.get(
            f"{base_url}/analyst-estimates/{ticker}",
            params={
                "symbol": ticker,
                "period": "quarter",
                "apikey": api_key,
            }
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            raise ValueError(f"No forecast data found for ticker {ticker}")
        
        # Process the data
        df = pd.DataFrame(data)
        
        # Rename columns to match historical data
        column_mapping = {
            'revenueAvg': 'Total Revenue',
            'sgaExpenseAvg': 'Total Expenses',
            'ebitdaAvg': 'Net Income',
            'epsAvg': 'EPS',
        }
        
        df = df.rename(columns=column_mapping)
        df['Gross Profit'] = None  # FMP doesn't provide gross profit estimates
                
        return df
    
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching forecast data for {ticker}: {str(e)}")


def financial_statement(ticker: str,) -> pd.DataFrame:
    """
    Combine historical and forecast financial data into a single DataFrame
    with financial metrics as index and years as columns (accounting style).
    
    Args:
        historical_data (pd.DataFrame): Historical financial data from fetch_financial_data
        forecast_data (pd.DataFrame): Forecast data from fetch_financial_forecast
    
    Returns:
        pd.DataFrame: Combined data with:
            - Index: Financial metrics (Revenue, GrossProfit, etc.)
            - Columns: Years (historical followed by forecast)
    """
    # Create copies to avoid modifying original DataFrames
    hist_df = fetch_financial_data(ticker)
    # fcst_df = fetch_financial_forecast(ticker)
    # hist_df = pd.concat([hist_df, fcst_df])

    hist_df = hist_df.T.reset_index().rename(columns={'index': 'Date'})
    
    # Extract year from dates and create year-period columns
    hist_df['Year'] = pd.to_datetime(hist_df['Date']).dt.year
    hist_df['Period'] = pd.to_datetime(hist_df['Date']).dt.quarter
    
    # Create list of metrics (excluding Date, Year, Period columns)
    metrics = [col for col in hist_df.columns if col not in ['Date', 'Year', 'Period']]
        
    # Aggregate historical and forecast data by year
    hist_yearly = hist_df.groupby('Year', as_index=True)[metrics].sum()

    # Sort index to ensure historical years come before forecast years
    df = hist_yearly.sort_values('Year')
    
    # Add suffixes to forecast years
    # forecast_years = fore_yearly.index
    # df = df.rename(columns=lambda x: f"{x} (F)" if x in forecast_years else str(x))
    
    # Format numeric columns
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            df[col] = df[col].round(2)
    
    return df.reset_index()


def fetch_stock_data(
    ticker: str,
    start_date: Optional[Union[str, datetime, date]] = None,
    days: Optional[int] = None,
    end_date: Optional[Union[str, datetime, date]] = None
) -> pd.DataFrame:
    """
    Fetch daily stock data for a given ticker from Yahoo Finance.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple)
        start_date (Optional[Union[str, datetime, date]]): Start date for data fetch.
            Can be string 'YYYY-MM-DD', datetime, or date object.
        days (Optional[int]): Number of days to fetch from start_date.
            If provided with start_date, end_date will be calculated.
        end_date (Optional[Union[str, datetime, date]]): End date for data fetch.
            Defaults to current date if not specified.
    
    Returns:
        pd.DataFrame: DataFrame containing stock data with columns:
            - Date
            - Ticker
            - Open
            - High
            - Low
            - Close
            - Volume
            - Dividends
            - ema50
            - ema200
            - yield
    
    Raises:
        ValueError: If the ticker is invalid or if data cannot be fetched
    """
    # Create ticker object
    stock = yf.Ticker(ticker)
    
    # Handle end_date
    if end_date is None:
        end_date = datetime.now().date()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # Handle start_date and days
    if start_date is not None:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        if days is not None:
            end_date = start_date + timedelta(days=days)
    elif days is not None:
        start_date = end_date - timedelta(days=days)
    else:
        # Default to last year if no parameters specified
        start_date = end_date - timedelta(days=365)
    
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
    
    # Process the dataframe
    df = (df.reset_index()
        [['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends']]
    )
    df.insert(1, 'Ticker', ticker)
    df.Date = df.Date.dt.date

    # Calculate technical indicators
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

def get_tickers() -> pd.DataFrame:
    from io import StringIO
    import requests

    response = requests.get("https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=demo")
    data = response.text
    df = pd.read_csv(StringIO(data))

    df['name'] = df['name'].fillna('')

    df.rename(columns={
        'symbol': 'Ticker',
        'name': 'Company Name',
        'exchange': 'Exchange',
        'assetType': 'Asset Type',
        'ipoDate': 'IPO Date'
    }, inplace=True)

    df.drop(columns=['delistingDate', 'status'], inplace=True)

    df.to_sql('tickers', if_exists='replace', index=False, con='sqlite:///database.db')
    
    return df


def get_sp500_tickers(save_locally: bool = False) -> pd.DataFrame:
    """
    Fetch the current list of S&P 500 companies from Wikipedia.
    
    Returns:
        pd.DataFrame: DataFrame containing S&P 500 companies with columns:
            - Symbol: Stock ticker
            - Security: Company name
            - GICS Sector: Industry sector
            - GICS Sub-Industry: Specific industry category
            - Headquarters Location: Company HQ location
            - Date Added: When stock was added to S&P 500
            - CIK: SEC Central Index Key
    
    Raises:
        ValueError: If unable to fetch or parse the Wikipedia table
    """
    import ssl
    from bs4 import BeautifulSoup
    
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    try:
        # Create a custom SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        
        # Fetch the page with SSL context
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first table (S&P 500 companies table)
        table = soup.find('table', {'class': 'wikitable'})
        
        # Extract headers
        headers = []
        for th in table.find_all('th'):
            header = th.text.strip()
            headers.append(header)
        
        # Extract rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            if row:  # Skip empty rows
                rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Clean up the data
        df = df.rename(columns={
            'Symbol': 'Ticker',
            'Security': 'Company Name',
            'GICS Sector': 'Sector',
            'GICS Sub-Industry': 'Industry',
            'Headquarters Location': 'Location',
            'Date added': 'Date Added',
        })
        
        # Clean and convert data types
        df['Ticker'] = df['Ticker'].str.strip()
        df['CIK'] = df['CIK'].astype(str).str.zfill(10)
        df['Date Added'] = pd.to_datetime(df['Date Added'], errors='coerce')
        
        if save_locally:
            # Cache the results
            os.makedirs('data', exist_ok=True)
            df.to_csv('data/sp500_companies.csv', index=False)
        
        return df
        
    except Exception as e:
        # Try to load cached data if available
        try:
            if os.path.exists('data/sp500_companies.csv'):
                print("Warning: Using cached S&P 500 data due to fetch error")
                return pd.read_csv('data/sp500_companies.csv')
        except:
            pass
        
        raise ValueError(f"Error fetching S&P 500 companies: {str(e)}")


def get_snp_market_caps(sp: pd.DataFrame) -> pd.DataFrame:
    """
    Get market capitalizations for S&P 500 companies.

    Args:
        sp (pd.DataFrame): DataFrame containing S&P 500 tickers.

    Returns:
        dict: Dictionary mapping ticker symbols to their market capitalizations.
    """
    all = yf.Tickers(' '.join(sp['Ticker'].tolist()))

    return {ticker: info.fast_info.get('marketCap', None) for ticker, info in all.tickers.items()}


def get_qqq_tickers() -> pd.DataFrame:
    """
    Load QQQ (Nasdaq-100) components from the local CSV file.

    https://companiesmarketcap.com/invesco-qqq-trust/holdings/
    
    Returns:
        pd.DataFrame: DataFrame containing QQQ companies with columns:
            - Company Name: Company name
            - Index Weight: Weight in the index as percentage
    """
    try:
        df = pd.read_csv('data/qqq_companies.csv')
        # Convert Index Weight from string percentage to float
        df['Index Weight'] = df['Index Weight'].str.rstrip('%').astype('float') / 100.0
        return df
    except Exception as e:
        raise ValueError(f"Error loading QQQ companies data: {str(e)}")
