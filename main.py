import numpy as np

from fastapi import FastAPI

from src.datamodels import TickerRequest, VaRRequest, PortfolioVaRRequest
from src.data import fetch_stock_data
from src.visualization import plot_stock_analysis
from src.metrics import (
    historical_var,
    parametric_var,
    calculate_portfolio_returns,
    portfolio_var
)

app = FastAPI()

@app.post("/")
async def get_ticker(
    request: TickerRequest
):
    df = fetch_stock_data(
        request.ticker,
        days=request.days,
        end_date=request.end_date
    )

    fig = plot_stock_analysis(
        df,
        show_volume=True,
        show_yield=True,
    )

    return {
        'html': fig.to_html(),
    }

@app.post("/var-simulation")
async def var_simulation(
    request: VaRRequest
):
    return {
        "historical_var": historical_var(
            request.returns,
            confidence_level=request.confidence_level,
            investment_value=request.investment_value
        ),
        "parametric_var": parametric_var(
            request.returns,
            confidence_level=request.confidence_level,
            investment_value=request.investment_value
        ),
    }

@app.post("/var-simulation-portfolio")
async def portfolio_var_simulation(
    request: PortfolioVaRRequest
):
    """Calculate VaR for a portfolio of stocks."""
    # Validate weights sum to 1
    if not 0.99 <= sum(request.weights) <= 1.01:
        raise ValueError("Portfolio weights must sum to 1")
        
    # Fetch historical data for all stocks
    stock_data = {}
    for ticker in request.tickers:
        df = fetch_stock_data(ticker, days=request.days)
        stock_data[ticker] = df['Close'].values
        
    # Calculate returns for the portfolio
    returns = calculate_portfolio_returns(stock_data, np.array(request.weights))
    
    # Calculate VaR and risk metrics
    risk_metrics = portfolio_var(
        returns=returns,
        weights=np.array(request.weights),
        confidence_level=request.confidence_level,
        investment_value=request.investment_value,
        method=request.method
    )
    
    # Add portfolio composition to response
    risk_metrics["portfolio_composition"] = {
        ticker: weight
        for ticker, weight in zip(request.tickers, request.weights)
    }
    
    return risk_metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)