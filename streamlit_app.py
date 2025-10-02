"""
Streamlit frontend for VaR simulation and stock analysis.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"

# Import local modules
from src.data import fetch_stock_data
from src.visualization import plot_stock_analysis
from src.metrics import (
    historical_var,
    parametric_var,
    calculate_returns,
    portfolio_var
)

# Page config
st.set_page_config(
    page_title="VaR Simulation",
    page_icon="📈",
    layout="wide"
)

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose Analysis",
    ["Home", "Stock Analysis", "Single Asset VaR", "Portfolio VaR"]
)


# Home page
if page == "Home":
    st.title("VaR Simulation and Stock Analysis")
    st.write("""
    Welcome to the VaR Simulation tool! This application helps you analyze stocks and calculate Value at Risk (VaR) 
    for both individual assets and portfolios.
    
    Choose an analysis type from the sidebar to get started:
    - **Stock Analysis**: Analyze historical price data and trends for individual stocks
    - **Single Asset VaR**: Calculate VaR for a single asset using historical returns
    - **Portfolio VaR**: Calculate VaR for a portfolio of multiple assets
    """)

# Stock Analysis page
elif page == "Stock Analysis":
    st.title("Stock Analysis")
    
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1:
        ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
    with col2:
        days = st.number_input("Historical Days", min_value=1, value=252)
    with col3:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    if st.button("Analyze Stock"):
        with st.spinner("Fetching data..."):
            result = {
                'html': plot_stock_analysis(
                    fetch_stock_data(
                        ticker,
                        days=int(days) if days else 365,
                        end_date=end_date if end_date else None
                    ),
                    show_volume=True,
                    show_yield=True,
                )
            }
            if result and 'html' in result:
                st.plotly_chart(go.Figure(result['html']), use_container_width=True)

# Single Asset VaR page
elif page == "Single Asset VaR":
    st.title("Single Asset VaR Analysis")
    
    st.write("""
    Calculate Value at Risk (VaR) for a single asset using historical returns.
    Enter your returns series and parameters below.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        returns_input = st.text_area(
            "Returns Series",
            help="Enter return values, one per line or comma-separated (e.g., 0.02, -0.01, 0.03)"
        )
        
    with col2:
        confidence_level = st.slider(
            "Confidence Level",
            min_value=0.8,
            max_value=0.99,
            value=0.95,
            step=0.01,
            help="Confidence level for VaR calculation (e.g., 0.95 for 95%)"
        )
        
        investment_value = st.number_input(
            "Investment Value",
            min_value=0.0,
            value=1.0,
            step=0.1,
            help="Current investment value"
        )
    
    if st.button("Calculate VaR"):
        if returns_input:
            # Parse returns
            returns = [float(x.strip()) for x in returns_input.replace('\n', ',').split(',')
                      if x.strip()]
            
            if returns:
                with st.spinner("Calculating VaR..."):
                    result = {
                        'historical_var': historical_var(returns, confidence_level, investment_value),
                        'parametric_var': parametric_var(returns, confidence_level, investment_value),
                    }
                    if result:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Historical VaR",
                                f"{result['historical_var']:.2f}",
                                help="Maximum potential loss using historical simulation"
                            )
                        with col2:
                            st.metric(
                                "Parametric VaR",
                                f"{result['parametric_var']:.2f}",
                                help="Maximum potential loss assuming normal distribution"
                            )
            else:
                st.error("Please enter valid returns values")

# Portfolio VaR page
elif page == "Portfolio VaR":
    st.title("Portfolio VaR Analysis")
    
    st.write("""
    Calculate Value at Risk (VaR) for a portfolio of stocks.
    Add stocks and their weights, then choose your VaR calculation parameters.
    """)
    
    # Portfolio composition
    st.subheader("Portfolio Composition")
    
    num_assets = st.number_input("Number of Assets", min_value=1, max_value=10, value=3)
    
    tickers = []
    weights = []
    
    cols = st.columns(2)
    
    for i in range(num_assets):
        with cols[0]:
            ticker = st.text_input(f"Stock {i+1} Ticker", key=f"ticker_{i}").upper()
            tickers.append(ticker)
        with cols[1]:
            weight = st.number_input(
                f"Stock {i+1} Weight",
                min_value=0.0,
                max_value=1.0,
                value=1.0/num_assets,
                step=0.01,
                key=f"weight_{i}"
            )
            weights.append(weight)
    
    # VaR parameters
    st.subheader("VaR Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days = st.number_input("Historical Days", min_value=1, value=252, max_value=500)
        
    with col2:
        confidence_level = st.slider(
            "Confidence Level",
            min_value=0.8,
            max_value=0.99,
            value=0.95,
            step=0.01
        )
        
    with col3:
        investment_value = st.number_input(
            "Total Investment Value USD",
            min_value=0,
            value=100000,
            step=1000
        )
        
    method = st.selectbox(
        "VaR Calculation Method",
        ["historical", "parametric"],
        help="Choose between historical simulation or parametric (normal distribution) method"
    )
    
    if st.button("Calculate Portfolio VaR"):
        # Validate inputs
        if not all(tickers) or not all(weights):
            st.error("Please fill in all tickers and weights")
        elif not sum(weights) - 1.00 <= 0.001:
            st.error("Weights must sum to 1")
        else:
            with st.spinner("Calculating Portfolio VaR..."):
                try:
                    # Fetch data for all stocks
                    all_returns = pd.DataFrame()
                    
                    for ticker, weight in zip(tickers, weights):
                        df = fetch_stock_data(ticker, days=days)
                        if df.empty:
                            raise ValueError(f"No data found for ticker {ticker}")
                        
                        # Calculate returns for this stock
                        stock_returns = pd.Series(
                            calculate_returns(df['Close'].values), 
                            name=ticker
                        )
                        all_returns[ticker] = stock_returns

                    # Calculate VaR and risk metrics
                    var_result = portfolio_var(
                        returns=all_returns,
                        weights=np.array(weights),
                        confidence_level=confidence_level,
                        investment_value=investment_value,
                        method=method
                    )

                    # Calculate additional portfolio metrics
                    portfolio_returns = all_returns.dot(weights)
                    portfolio_mean = portfolio_returns.mean()
                    portfolio_std = portfolio_returns.std()
                    
                    result = {
                        'var': var_result,
                        'portfolio_returns': portfolio_returns,
                        'daily_mean': portfolio_mean,
                        'daily_std': portfolio_std,
                        'annualized_return': portfolio_mean * 252,
                        'annualized_std': portfolio_std * np.sqrt(252),
                        'sharpe_ratio': (portfolio_mean / portfolio_std) * np.sqrt(252) if portfolio_std != 0 else 0
                    }

                    # Display results
                    if result is not None:
                        col1, col2 = st.columns(2)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                f"Portfolio VaR ({method})",
                                f"${float(result['var']):,.2f}",
                                help=f"Maximum potential loss at {confidence_level*100}% confidence level"
                            )
                            st.metric(
                                "Daily Volatility",
                                f"{result['daily_std']*100:.2f}%",
                                help="Standard deviation of daily returns"
                            )
                            
                        with col2:
                            st.metric(
                                "Expected Annual Return",
                                f"{result['annualized_return']*100:.2f}%",
                                help="Annualized expected return based on historical data"
                            )
                            st.metric(
                                "Annual Volatility",
                                f"{result['annualized_std']*100:.2f}%",
                                help="Annualized standard deviation of returns"
                            )
                            
                        with col3:
                            st.metric(
                                "Sharpe Ratio",
                                f"{result['sharpe_ratio']:.2f}",
                                help="Risk-adjusted return measure (higher is better)"
                            )
                            
                        # Display additional portfolio metrics
                        st.subheader("Portfolio Composition")
                        composition_df = pd.DataFrame({
                            'Ticker': tickers,
                            'Weight': [f"{w*100:.1f}%" for w in weights],
                            'Investment Amount': [f"${w*investment_value:,.2f}" for w in weights]
                        })
                        st.table(composition_df)
                        
                        # Display returns statistics
                        st.subheader("Returns Statistics")
                        returns_stats = pd.DataFrame({
                            'Daily Mean': [f"{all_returns[ticker].mean()*100:.2f}%" for ticker in tickers],
                            'Daily Std Dev': [f"{all_returns[ticker].std()*100:.2f}%" for ticker in tickers],
                            'Min Return': [f"{all_returns[ticker].min()*100:.2f}%" for ticker in tickers],
                            'Max Return': [f"{all_returns[ticker].max()*100:.2f}%" for ticker in tickers]
                        }, index=tickers)
                        st.table(returns_stats)

                except Exception as e:
                    st.error(f"Error calculating portfolio VaR: {str(e)}")
                    st.stop()