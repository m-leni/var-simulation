from pydantic import BaseModel

from typing import List, Union

class TickerRequest(BaseModel):
    ticker: str
    days: int = 365
    end_date: str | None = None

class VaRRequest(BaseModel):
    returns: List[float]
    confidence_level: float = 0.95
    investment_value: float = 1.0

class PortfolioVaRRequest(BaseModel):
    tickers: List[str]
    weights: List[float]
    days: int = 252  # Default to 1 trading year
    confidence_level: float = 0.95
    investment_value: float = 100000.0
    method: str = "historical"  # "historical" or "parametric"