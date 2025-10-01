"""
This module provides functions for financial data visualization using plotly.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

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
            x=df.index,
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
                x=df.index,
                y=df['ema50'],
                name='EMA 50',
                line=dict(color='rgba(255, 165, 0, 0.8)', width=1.5)
            ),
            row=1, col=1
        )

    if 'ema200' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
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
                x=df.index,
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
                x=df.index,
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