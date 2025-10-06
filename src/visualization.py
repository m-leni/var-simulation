"""
This module provides functions for financial data visualization using plotly.
"""
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from typing import Optional, List, Union

def plot_stock_analysis(
    df: pd.DataFrame,
    title: Optional[str] = None,
    show_volume: bool = True,
    show_yield: bool = True,
    height: int = 1000
) -> go.Figure:
    """
    Create an interactive candlestick chart with EMA indicators and volume.
    
    Args:
        df (pd.DataFrame): DataFrame containing OHLCV data and EMA indicators.
            Required columns: ['Open', 'High', 'Low', 'Close']
            Optional columns: ['Volume', 'ema50', 'ema200']
        title (Optional[str]): Title for the chart
        show_volume (bool): Whether to show volume subplot
        height (int): Height of the figure in pixels
    
    Returns:
        go.Figure: Plotly figure object containing the chart
    """
    # Determine number of subplots needed
    n_rows = 1
    row_heights = [0.6]
    subplot_titles = ['']
    
    if show_yield and 'yield' in df.columns:
        n_rows += 1
        row_heights.extend([0.2])
        subplot_titles.extend(['Cumulative Yield (%)'])
        
    if show_volume and 'Volume' in df.columns:
        n_rows += 1
        row_heights.extend([0.2])
        subplot_titles.extend(['Volume'])
    
    # Create figure with subplots
    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=subplot_titles,
        row_heights=row_heights
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add EMA indicators if they exist
    if 'ema50' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['ema50'],
                name='EMA 50',
                line=dict(color='rgba(255, 165, 0, 0.8)', width=1.5)
            ),
            row=1, col=1
        )

    if 'ema200' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['ema200'],
                name='EMA 200',
                line=dict(color='rgba(46, 139, 87, 0.8)', width=1.5)
            ),
            row=1, col=1
        )

    # Add cumulative yield if requested
    current_row = 2
    if show_yield and 'yield' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['yield'],
                name='Cumulative Yield',
                line=dict(color='blue', width=2),
                fill='tozeroy'
            ),
            row=current_row, col=1
        )
        current_row += 1

    # Add volume bars if requested
    if show_volume and 'Volume' in df.columns:
        colors = ['red' if row['Open'] > row['Close'] else 'green' 
                 for _, row in df.iterrows()]
        
        fig.add_trace(
            go.Bar(
                x=df['Date'],
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                marker_line_width=0,
                opacity=0.8
            ),
            row=current_row, col=1
        )

    # Update layout
    fig.update_layout(
        title=title or 'Stock Analysis',
        yaxis_title='Price',
        yaxis2_title='Volume' if show_volume else None,
        xaxis_rangeslider_visible=False,
        height=height,
        template='plotly_white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Update y-axes labels
    current_row = 1
    fig.update_yaxes(title_text="Price", row=current_row, col=1)
    
    if show_yield and 'yield' in df.columns:
        current_row += 1
        fig.update_yaxes(title_text="Yield %", row=current_row, col=1)
    
    if show_volume and 'Volume' in df.columns:
        current_row += 1
        fig.update_yaxes(title_text="Volume", row=current_row, col=1)

    # Add range selector buttons similar to TradingView (7D, 1M, 3M, 6M, YTD, 1Y, All)
    fig.update_xaxes(
        rangeslider=dict(visible=False),
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="7D", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        type="date"
    )

    return fig

def plot_financial_metrics(
    df: pd.DataFrame,
    metrics: Union[str, List[str]],
    title: Optional[str] = None,
    height: int = 600,
    show_growth: bool = True
) -> go.Figure:
    """
    Create an interactive line chart showing the evolution of financial metrics over time.
    
    Args:
        df (pd.DataFrame): DataFrame with financial data where:
            - 'Year' is a column
            - Other columns are financial metrics
        metrics (Union[str, List[str]]): Single metric or list of metrics to plot
            Valid metrics: Column names in the DataFrame (e.g., 'Total Revenue', 'EBITDA', etc.)
        title (Optional[str]): Title for the chart
        height (int): Height of the figure in pixels
        show_growth (bool): Whether to show YoY growth rates on secondary y-axis
    
    Returns:
        go.Figure: Plotly figure object containing the chart
    """
    # Convert single metric to list
    if isinstance(metrics, str):
        metrics = [metrics]
    
    # Validate metrics
    available_metrics = [col for col in df.columns if col != 'Year']
    for metric in metrics:
        if metric not in available_metrics:
            raise ValueError(f"Invalid metric: {metric}. Must be one of {available_metrics}")
    
    # Create figure with secondary y-axis if showing growth
    fig = make_subplots(specs=[[{"secondary_y": show_growth}]])
    
    # Color palette for multiple metrics
    colors = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 
              'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
              'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
              'rgb(227, 119, 194)', 'rgb(127, 127, 127)']
    
    for i, metric in enumerate(metrics):
        # Extract years and values
        years = df['Year'].values
        values = df[metric].values
        
        # Plot the metric evolution
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                name=metric,
                line=dict(color=colors[i % len(colors)]),
                legendgroup=metric
            ),
            secondary_y=False
        )
        
        # Calculate and plot YoY growth if requested
        if show_growth:
            # Handle NaN and inf values in growth calculation
            growth_values = np.diff(values) / values[:-1] * 100
            growth_values = np.where(np.isinf(growth_values), np.nan, growth_values)
            growth_years = years[1:]
            
            fig.add_trace(
                go.Scatter(
                    x=growth_years,
                    y=growth_values,
                    name=f"{metric} YoY Growth %",
                    line=dict(
                        color=colors[i % len(colors)],
                        width=1,
                        dash='dot'
                    ),
                    legendgroup=metric,
                    showlegend=len(metrics) == 1  # Only show if single metric
                ),
                secondary_y=True
            )
    
    # Format hover template
    hover_template = (
        "<b>%{x}</b><br>" +
        "%{fullData.name}: %{y:,.2f}<br><extra></extra>"
    )
    
    # Update traces with hover template
    for trace in fig.data:
        if not trace.name.endswith("Growth %"):
            trace.hovertemplate = hover_template
        else:
            trace.hovertemplate = "<b>%{x}</b><br>%{y:.1f}%<br><extra></extra>"
    
    # Update layout
    fig.update_layout(
        title=title or f"Financial Metrics Evolution: {', '.join(metrics)}",
        height=height,
        hovermode='x unified',
        legend=dict(
            groupclick="toggleitem"
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    # Format axis labels with comma separator for thousands
    fig.update_xaxes(
        title_text="Year",
        tickmode='linear',
        dtick=1  # Show every year
    )
    fig.update_yaxes(
        title_text="Amount (USD)",
        secondary_y=False,
        tickformat=",",  # Add commas for thousands
        showgrid=True
    )
    if show_growth:
        fig.update_yaxes(
            title_text="YoY Growth (%)",
            secondary_y=True,
            showgrid=False,
            zeroline=True
        )

    # Return the constructed figure
    return fig

def save_chart(
    fig: go.Figure,
    filename: str,
    format: str = 'html'
) -> None:
    """
    Save a plotly chart to a file.
    
    Args:
        fig (go.Figure): Plotly figure object to save
        filename (str): Name of the file to save to (without extension)
        format (str): Format to save in ('html' or 'png')
    """
    if format not in ['html', 'png']:
        raise ValueError("format must be either 'html' or 'png'")
    
    if format == 'html':
        fig.write_html(f"{filename}.html")
    else:
        fig.write_image(f"{filename}.png")