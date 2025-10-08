"""
Example usage of analyst forecast functions from yfinance.

This script demonstrates how to use the new analyst forecast functions
to fetch forward-looking data and calculate forward P/E ratios.
"""

from src.data import (
    fetch_analyst_price_targets,
    fetch_analyst_earnings_forecast,
    fetch_analyst_revenue_forecast,
    fetch_analyst_growth_estimates,
    get_forward_pe_data
)
from src.metrics import forward_pe_ratio


def main():
    ticker = "AAPL"
    
    print(f"Analyst Forecast Data for {ticker}")
    print("=" * 50)
    
    # 1. Get analyst price targets
    print("\n1. Analyst Price Targets:")
    try:
        targets = fetch_analyst_price_targets(ticker)
        print(f"   Current Price: ${targets.get('current', 'N/A'):.2f}")
        print(f"   Target Mean:   ${targets.get('mean', 'N/A'):.2f}")
        print(f"   Target Low:    ${targets.get('low', 'N/A'):.2f}")
        print(f"   Target High:   ${targets.get('high', 'N/A'):.2f}")
        print(f"   Target Median: ${targets.get('median', 'N/A'):.2f}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Get analyst earnings forecast
    print("\n2. Analyst Earnings (EPS) Forecast:")
    try:
        earnings = fetch_analyst_earnings_forecast(ticker)
        print(earnings)
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Get analyst revenue forecast
    print("\n3. Analyst Revenue Forecast:")
    try:
        revenue = fetch_analyst_revenue_forecast(ticker)
        print(revenue)
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Get growth estimates
    print("\n4. Analyst Growth Estimates:")
    try:
        growth = fetch_analyst_growth_estimates(ticker)
        print(growth)
    except Exception as e:
        print(f"   Error: {e}")
    
    # 5. Get forward P/E data (comprehensive)
    print("\n5. Forward P/E Data:")
    try:
        pe_data = get_forward_pe_data(ticker)
        print(f"   Current Price:  ${pe_data['current_price']:.2f}")
        print(f"   Forward EPS:    ${pe_data['forward_eps']:.2f}")
        print(f"   Forward P/E:    {pe_data['forward_pe']:.2f}")
        print(f"   Trailing P/E:   {pe_data['trailing_pe']:.2f}")
        print(f"   Target Price:   ${pe_data['target_price']:.2f}")
        print(f"   # Analysts:     {pe_data['num_analysts']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. Calculate forward P/E manually
    print("\n6. Manual Forward P/E Calculation:")
    try:
        current_price = 150.0  # Example
        forward_eps = 6.0      # Example
        pe = forward_pe_ratio(current_price, forward_eps)
        print(f"   Price: ${current_price}, Forward EPS: ${forward_eps}")
        print(f"   Forward P/E: {pe:.2f}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
