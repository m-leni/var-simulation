"""
Terminal User Interface (TUI) components for stock analysis using Textual.
This module contains all TUI-specific widgets and the main application class.
"""
import sqlite3 as sql
from datetime import date, timedelta
from typing import Optional

import pandas as pd
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)
from textual.binding import Binding

from src.data import fetch_stock_data
from src.database import create_db, insert_to_stock_data


class StockMetricsDisplay(Static):
    """Widget to display stock metrics."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {}
    
    def update_metrics(self, df: pd.DataFrame, ticker: str):
        """Update metrics display with stock data."""
        if df.empty:
            self.update("No data available")
            return
        
        latest = df.iloc[-1]
        first = df.iloc[0]
        
        # Calculate metrics
        latest_price = latest['Close']
        price_change = latest_price - first['Close']
        price_change_pct = (price_change / first['Close']) * 100
        volume = latest['Volume']
        high = df['High'].max()
        low = df['Low'].min()
        avg_volume = df['Volume'].mean()
        
        # Build metrics display
        metrics_text = f"""[bold cyan]{ticker} - Stock Metrics[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]Latest Price:[/bold] ${latest_price:.2f}
[bold]Price Change:[/bold] ${price_change:+.2f} ({price_change_pct:+.2f}%)
[bold]Volume:[/bold] {volume:,.0f}
[bold]Avg Volume:[/bold] {avg_volume:,.0f}
[bold]Period High:[/bold] ${high:.2f}
[bold]Period Low:[/bold] ${low:.2f}
[bold]Date Range:[/bold] {df.iloc[0]['Date']} to {df.iloc[-1]['Date']}
[bold]Total Records:[/bold] {len(df)}
"""
        self.update(metrics_text)


class StockAnalysisApp(App):
    """A Textual app for stock analysis."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #input-container {
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }
    
    #metrics-container {
        height: auto;
        padding: 1;
        margin-top: 1;
        background: $panel;
        border: solid $accent;
    }
    
    #table-container {
        height: 1fr;
        padding: 1;
        margin-top: 1;
        background: $panel;
        border: solid $success;
    }
    
    Input {
        width: 100%;
        margin-bottom: 1;
    }
    
    Button {
        margin: 1;
    }
    
    DataTable {
        height: 100%;
    }
    
    StockMetricsDisplay {
        height: auto;
        padding: 1;
    }
    
    Label {
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh Data"),
    ]
    
    def __init__(self):
        super().__init__()
        self.conn = sql.connect("database.db")
        create_db(conn=self.conn)
        self.current_df = None
        self.current_ticker = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        with Container(id="input-container"):
            yield Label("[bold]Stock Analysis - TUI[/bold]")
            yield Label("Enter a stock ticker and number of days:")
            yield Input(placeholder="Ticker (e.g., AAPL)", id="ticker-input")
            yield Input(placeholder="Days (e.g., 252)", id="days-input", value="252")
            with Horizontal():
                yield Button("Fetch Data", variant="primary", id="fetch-button")
                yield Button("Clear", variant="default", id="clear-button")
        
        with Container(id="metrics-container"):
            yield StockMetricsDisplay(id="metrics-display")
        
        with VerticalScroll(id="table-container"):
            yield DataTable(id="stock-table")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Set up the data table when app starts."""
        table = self.query_one("#stock-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Initial message
        metrics = self.query_one("#metrics-display", StockMetricsDisplay)
        metrics.update("[dim]Enter a ticker and click 'Fetch Data' to begin[/dim]")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "fetch-button":
            self.fetch_stock_data()
        elif event.button.id == "clear-button":
            self.clear_data()
    
    def action_refresh(self) -> None:
        """Refresh the current stock data."""
        if self.current_ticker:
            self.fetch_stock_data()
    
    def fetch_stock_data(self) -> None:
        """Fetch stock data based on user input."""
        ticker_input = self.query_one("#ticker-input", Input)
        days_input = self.query_one("#days-input", Input)
        
        ticker = ticker_input.value.strip().upper()
        
        if not ticker:
            self.notify("Please enter a ticker symbol", severity="error")
            return
        
        try:
            days = int(days_input.value) if days_input.value else 252
        except ValueError:
            self.notify("Days must be a number", severity="error")
            return
        
        if days < 1 or days > 500:
            self.notify("Days must be between 1 and 500", severity="error")
            return
        
        # Show loading notification
        self.notify(f"Fetching data for {ticker}...", timeout=2)
        
        try:
            # Calculate dates
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Try to fetch from database first
            df = pd.read_sql(f"""
                SELECT * 
                FROM daily_stock_price 
                WHERE Ticker = '{ticker}' 
                    AND Date BETWEEN DATE('now', '-{days} days') AND DATE('now')
            """, con=self.conn)
            
            # If not in DB or incomplete, fetch from API
            if df.empty or df.Date.min() != str(date.today() - timedelta(days)):
                df = fetch_stock_data(
                    ticker,
                    start_date=start_date,
                    end_date=end_date
                )
                insert_to_stock_data(df, self.conn)
            
            if df.empty:
                self.notify(f"No data found for {ticker}", severity="error")
                return
            
            # Store current data
            self.current_df = df
            self.current_ticker = ticker
            
            # Update the display
            self.update_display(df, ticker)
            self.notify(f"Successfully loaded {len(df)} records for {ticker}", severity="information")
            
        except Exception as e:
            self.notify(f"Error fetching data: {str(e)}", severity="error")
    
    def update_display(self, df: pd.DataFrame, ticker: str) -> None:
        """Update the metrics and table display with new data."""
        # Update metrics
        metrics = self.query_one("#metrics-display", StockMetricsDisplay)
        metrics.update_metrics(df, ticker)
        
        # Update table
        table = self.query_one("#stock-table", DataTable)
        table.clear(columns=True)
        
        # Add columns
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for col in columns:
            if col in df.columns:
                table.add_column(col, key=col)
        
        # Add rows (show latest 50 to avoid performance issues)
        display_df = df.tail(50)
        for _, row in display_df.iterrows():
            row_data = []
            for col in columns:
                if col in df.columns:
                    value = row[col]
                    if col == 'Date':
                        row_data.append(str(value))
                    elif col == 'Volume':
                        row_data.append(f"{value:,.0f}")
                    else:
                        row_data.append(f"{value:.2f}")
            table.add_row(*row_data)
    
    def clear_data(self) -> None:
        """Clear all displayed data."""
        table = self.query_one("#stock-table", DataTable)
        table.clear(columns=True)
        
        metrics = self.query_one("#metrics-display", StockMetricsDisplay)
        metrics.update("[dim]Data cleared. Enter a ticker to begin.[/dim]")
        
        ticker_input = self.query_one("#ticker-input", Input)
        days_input = self.query_one("#days-input", Input)
        ticker_input.value = ""
        days_input.value = "252"
        
        self.current_df = None
        self.current_ticker = None
        
        self.notify("Data cleared", severity="information")


def run_tui():
    """Run the TUI application."""
    app = StockAnalysisApp()
    app.run()
