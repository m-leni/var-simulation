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

# Helper functions
def fetch_stock_data(ticker: str, days: int = 252, end_date: str = None):
    """Fetch stock data from the API."""
    response = requests.post(
        f"{API_BASE_URL}/",
        headers={"Content-Type": "application/json"},
        json={
            "ticker": ticker,
            "days": days,
            "end_date": end_date
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data: {response.json().get('detail', 'Unknown error')}")
        return None

def calculate_var(returns, confidence_level: float = 0.95, investment_value: float = 1.0):
    """Calculate VaR using the API."""
    response = requests.post(
        f"{API_BASE_URL}/var-simulation",
        headers={"Content-Type": "application/json"},
        json={
            "returns": returns,
            "confidence_level": confidence_level,
            "investment_value": investment_value
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error calculating VaR: {response.json().get('detail', 'Unknown error')}")
        return None

def calculate_portfolio_var(tickers, weights, days=252, confidence_level=0.95, 
                          investment_value=100000, method="historical"):
    """Calculate portfolio VaR using the API."""
    response = requests.post(
        f"{API_BASE_URL}/portfolio-var",
        headers={"Content-Type": "application/json"},
        json={
            "tickers": tickers,
            "weights": weights,
            "days": days,
            "confidence_level": confidence_level,
            "investment_value": investment_value,
            "method": method
        }
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error calculating portfolio VaR: {response.json().get('detail', 'Unknown error')}")
        return None

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
            result = fetch_stock_data(ticker, days, end_date.strftime("%Y-%m-%d"))
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
                    result = calculate_var(returns, confidence_level, investment_value)
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
                st.error("Please enter valid return values")

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
        days = st.number_input("Historical Days", min_value=1, value=252)
        
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
            "Total Investment Value",
            min_value=0.0,
            value=100000.0,
            step=1000.0
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
        elif not 0.99 <= sum(weights) <= 1.01:
            st.error("Weights must sum to 1")
        else:
            with st.spinner("Calculating Portfolio VaR..."):
                result = calculate_portfolio_var(
                    tickers, weights, days, confidence_level,
                    investment_value, method
                )
                
                if result:
                    # Display results in an organized way
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Value at Risk (VaR)", f"${result['var']:,.2f}")
                        st.metric("Daily Volatility", f"{result['daily_volatility']*100:.2f}%")
                        
                    with col2:
                        st.metric("Expected Daily Return", f"{result['expected_return']*100:.2f}%")
                        st.metric("Annualized Volatility", f"{result['annualized_volatility']*100:.2f}%")
                        
                    with col3:
                        st.metric("Annualized Return", f"{result['annualized_return']*100:.2f}%")
                        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
                    
                    # Portfolio composition table
                    st.subheader("Portfolio Composition")
                    composition_df = pd.DataFrame({
                        'Ticker': result['portfolio_composition'].keys(),
                        'Weight': [f"{w*100:.1f}%" for w in result['portfolio_composition'].values()]
                    })
                    st.table(composition_df)