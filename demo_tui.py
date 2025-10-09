"""
Demo script for TUI Stock Analysis.
This script shows how the TUI works with sample data.
"""
import pandas as pd
from datetime import date, timedelta
import random


def generate_sample_stock_data(ticker="AAPL", days=252):
    """
    Generate sample stock data for demonstration.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days of data to generate
        
    Returns:
        pd.DataFrame: Sample stock data
    """
    # Generate dates
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate sample OHLCV data with realistic patterns
    base_price = 150.0
    data = []
    
    for i, dt in enumerate(dates):
        # Add some trend and randomness
        trend = i * 0.05
        noise = random.uniform(-5, 5)
        
        close = base_price + trend + noise
        open_price = close + random.uniform(-2, 2)
        high = max(open_price, close) + random.uniform(0, 3)
        low = min(open_price, close) - random.uniform(0, 3)
        volume = random.randint(50000000, 150000000)
        
        data.append({
            'Date': dt.date(),
            'Open': round(open_price, 2),
            'High': round(high, 2),
            'Low': round(low, 2),
            'Close': round(close, 2),
            'Volume': volume,
            'Ticker': ticker
        })
    
    df = pd.DataFrame(data)
    
    # Calculate yield
    df['yield'] = ((df['Close'] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    return df


def demo_tui():
    """
    Demonstrate the TUI with sample data.
    """
    print("=" * 60)
    print("TUI Stock Analysis Demo")
    print("=" * 60)
    print()
    
    # Generate sample data
    ticker = "AAPL"
    days = 30
    print(f"Generating sample data for {ticker} (last {days} days)...")
    df = generate_sample_stock_data(ticker, days)
    
    print(f"\n✓ Successfully generated {len(df)} records")
    print("\nSample Data Preview:")
    print("-" * 60)
    print(df.head(10).to_string(index=False))
    
    print("\n\nStock Metrics:")
    print("-" * 60)
    
    latest = df.iloc[-1]
    first = df.iloc[0]
    
    latest_price = latest['Close']
    price_change = latest_price - first['Close']
    price_change_pct = (price_change / first['Close']) * 100
    volume = latest['Volume']
    high = df['High'].max()
    low = df['Low'].min()
    avg_volume = df['Volume'].mean()
    
    print(f"Ticker:          {ticker}")
    print(f"Latest Price:    ${latest_price:.2f}")
    print(f"Price Change:    ${price_change:+.2f} ({price_change_pct:+.2f}%)")
    print(f"Volume:          {volume:,.0f}")
    print(f"Avg Volume:      {avg_volume:,.0f}")
    print(f"Period High:     ${high:.2f}")
    print(f"Period Low:      ${low:.2f}")
    print(f"Date Range:      {df.iloc[0]['Date']} to {df.iloc[-1]['Date']}")
    print(f"Total Records:   {len(df)}")
    
    print("\n" + "=" * 60)
    print("TUI Application Features:")
    print("=" * 60)
    print("• Interactive ticker input")
    print("• Configurable date range")
    print("• Real-time data fetching with database caching")
    print("• Rich metrics display")
    print("• Scrollable data table")
    print("• Keyboard shortcuts (q=quit, r=refresh)")
    print("\nTo launch the TUI: uv run python tui_app.py")
    print("=" * 60)


if __name__ == "__main__":
    demo_tui()
