"""
Streamlit frontend for VaR simulation and stock analysis.
"""
import os
from dotenv import load_dotenv

import numpy as np
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import sqlite3 as sql
import streamlit as st

from src.data import (
    fetch_stock_data,
    financial_statement
)
from src.data import get_stock_info
from src.visualization import plot_stock_analysis, plot_financial_metrics
from src.metrics import (
    historical_var,
    parametric_var,
    calculate_returns,
    portfolio_var
)
from src.database import (
    create_db,
    insert_to_stock_data,
    insert_to_financial_data
)

CONN = sql.connect("database.db")

create_db(conn=CONN)

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
    Welcome to the VaR Simulation tool. This application allows you to:
    - Analyze stock price movements, fundamentals & financial performance
    - Calculate Value at Risk (VaR) for single assets
    - Analyze portfolio risk metrics
    """)

# Stock Analysis page
elif page == "Stock Analysis":
    st.title("Stock Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker = st.text_input("Enter Stock Ticker:", value="AAPL")
    
    with col2:
        date_option = st.radio(
            "Select Date Range:",
            ["Custom Range", "Last N Days"]
        )
    
    if date_option == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=252)
            )
        with col2:
            end_date = st.date_input("End Date", value=date.today())

        if start_date >= end_date:
            st.error("Error: End date must fall after start date.")

        days = (end_date - start_date).days

    elif date_option == "Last N Days":
        days = st.number_input(
            "Number of days:", 
            min_value=1, 
            value=252, 
            max_value=500
        )

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
    
    if st.button("Fetch stock data"):
        with st.spinner("Fetching data..."):
            try:
                # fetch data if exists in db
                df = pd.read_sql(f"""
                    SELECT * 
                    FROM daily_stock_price 
                    WHERE Ticker = '{ticker}' 
                        AND Date BETWEEN DATE('now', '-{days} days') AND DATE('now')
                """, con=CONN)

                if (df.empty) or (df.Date.min() != date.today()-timedelta(days)):
                    df = fetch_stock_data(
                        ticker, 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    insert_to_stock_data(df, CONN)

                fig = plot_stock_analysis(df, show_volume=True, show_yield=True)
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")

        # Financial Analysis Section
        st.subheader("Financial Analysis")
        
        try:
            with st.spinner("Fetching financial data..."):
                # fetch data if exists in db
                financial_df = pd.read_sql(f"""
                    SELECT *
                    FROM financial_data
                    WHERE Ticker = '{ticker}'
                """, con=CONN)

                # Fetch historical and forecast data
                financial_df = financial_statement(ticker)

                insert_to_financial_data(financial_df, ticker, CONN)

                financial_df.set_index('Year', inplace=True)
                financial_df.drop(columns=['Ticker'], inplace=True)
                        
                # Display the financial data
                st.write("Financial Metrics (in BUSD)")
                st.dataframe(
                    financial_df
                        #.style.format(':.2f', precision=2)
                        .style.background_gradient(cmap='RdYlGn', axis=0)
                )
                
                # Add some key insights
                st.write("### Key Insights")
                financial_df.reset_index(inplace=True)
                
                # Calculate year-over-year growth between the last two available years
                if 'Year' in financial_df.columns and len(financial_df) >= 2:
                    dfy = financial_df.copy()
                    dfy['Year'] = pd.to_numeric(dfy['Year'], errors='coerce')
                    dfy = dfy.dropna(subset=['Year']).sort_values('Year').reset_index(drop=True)
                    if len(dfy) >= 2:
                        prev = dfy.iloc[-2]
                        last = dfy.iloc[-1]
                        prev_year = int(prev['Year'])
                        last_year = int(last['Year'])

                        # Revenue growth
                        rev_prev = pd.to_numeric(prev.get('Total Revenue', None), errors='coerce')
                        rev_last = pd.to_numeric(last.get('Total Revenue', None), errors='coerce')
                        rev_growth = (rev_last / rev_prev - 1) * 100 if pd.notna(rev_prev) and rev_prev != 0 else None

                        # EBITDA growth (fallback to Gross Profit if EBITDA missing)
                        ebitda_prev = pd.to_numeric(prev.get('EBITDA', prev.get('Gross Profit', None)), errors='coerce')
                        ebitda_last = pd.to_numeric(last.get('EBITDA', last.get('Gross Profit', None)), errors='coerce')
                        ebitda_growth = (ebitda_last / ebitda_prev - 1) * 100 if pd.notna(ebitda_prev) and ebitda_prev != 0 else None

                        col1, col2 = st.columns(2)
                        with col1:
                            if rev_growth is None:
                                st.metric(f"Revenue {prev_year} → {last_year}", "n/a")
                            else:
                                st.metric(
                                    f"Revenue {prev_year} → {last_year}",
                                    f"{rev_last:,.2f}",
                                    delta=f"{rev_growth:.1f}%"
                                )
                        with col2:
                            if ebitda_growth is None:
                                st.metric(f"EBITDA {prev_year} → {last_year}", "n/a")
                            else:
                                st.metric(
                                    f"EBITDA {prev_year} → {last_year}",
                                    f"{ebitda_last:,.2f}",
                                    delta=f"{ebitda_growth:.1f}%"
                                )
                    else:
                        st.info("Not enough yearly financial data to compute Key Insights.")
                else:
                    st.info("Financial data not in expected yearly format (missing 'Year' column).")
                
                # Add metric visualization
                st.write("### Metric Evolution")
                metric = st.selectbox(
                    "Select metric to visualize:",
                    ["Total Revenue", "Total Expenses", "Gross Profit", "EBITDA", "Free Cash Flow", "Common Stock Dividend Paid", "Basic EPS"]
                )
                
                show_growth = st.checkbox("Show Year-over-Year Growth", value=True)
                
                fig = plot_financial_metrics(
                    financial_df,
                    metric,
                    title=f"{ticker} - {metric} Evolution",
                    show_growth=show_growth
                )
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error fetching financial data: {str(e)}")
        
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

                    # Align returns across tickers by dropping any rows with NaN
                    all_returns = all_returns.dropna()

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
                            
                        # Fetch company info for each ticker
                        info_map = {}
                        for t in tickers:
                            try:
                                info_map[t] = get_stock_info(t)
                            except Exception:
                                info_map[t] = {}

                        # Display additional portfolio metrics
                        st.subheader("Portfolio Composition")
                        composition_df = pd.DataFrame({
                            'Industry': [info_map.get(t, {}).get('industry', 'Unknown') for t in tickers],
                            'Sector': [info_map.get(t, {}).get('sector', 'Unknown') for t in tickers],
                            'Weight': [f"{w*100:.1f}%" for w in weights],
                            'Investment Amount': [f"${w*investment_value:,.2f}" for w in weights],
                        }, index=tickers)
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

                        # Aggregate exposure by Sector / Industry
                        st.subheader("Exposure by Sector / Industry")

                        group_by = st.selectbox("Group exposure by:", ["Industry", "Sector"]) 

                        # Build exposure DataFrame
                        exposure_rows = []
                        for t, w in zip(tickers, weights):
                            info = info_map.get(t, {})
                            sector = info.get('sector', 'Unknown')
                            industry = info.get('industry', 'Unknown')
                            exposure_rows.append({
                                'Ticker': t,
                                'Weight': w,
                                'Investment': w * investment_value,
                                'Sector': sector,
                                'Industry': industry
                            })

                        exposure_df = pd.DataFrame(exposure_rows)
                        if group_by == 'Sector':
                            agg = exposure_df.groupby('Sector').agg({
                                'Weight': 'sum',
                                'Investment': 'sum'
                            }).sort_values('Weight', ascending=False)
                        else:
                            agg = exposure_df.groupby('Industry').agg({
                                'Weight': 'sum',
                                'Investment': 'sum'
                            }).sort_values('Weight', ascending=False)

                        # Format and display
                        agg_display = agg.copy()
                        agg_display['Weight'] = (agg_display['Weight'] * 100).round(2).map(lambda x: f"{x}%")
                        agg_display['Investment'] = agg_display['Investment'].map(lambda x: f"${x:,.2f}")
                        st.table(agg_display)

                        # Show bar chart of weight exposure
                        st.bar_chart(agg['Weight'])

                except Exception as e:
                    st.error(f"Error calculating portfolio VaR: {str(e)}")
                    st.stop()