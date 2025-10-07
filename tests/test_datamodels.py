"""
Unit tests for src/datamodels.py module.
"""
import pytest
from pydantic import ValidationError
from src.datamodels import TickerRequest, VaRRequest, PortfolioVaRRequest


class TestTickerRequest:
    """Tests for TickerRequest model."""
    
    def test_valid_request(self):
        """Test valid ticker request."""
        request = TickerRequest(ticker="AAPL", days=365)
        assert request.ticker == "AAPL"
        assert request.days == 365
        assert request.end_date is None
        
    def test_default_days(self):
        """Test default value for days parameter."""
        request = TickerRequest(ticker="AAPL")
        assert request.days == 365
        
    def test_with_end_date(self):
        """Test with end_date parameter."""
        request = TickerRequest(ticker="AAPL", days=100, end_date="2024-01-01")
        assert request.end_date == "2024-01-01"
        
    def test_missing_ticker(self):
        """Test error when ticker is missing."""
        with pytest.raises(ValidationError):
            TickerRequest(days=365)
            
    def test_invalid_days_type(self):
        """Test error with invalid days type."""
        with pytest.raises(ValidationError):
            TickerRequest(ticker="AAPL", days="invalid")


class TestVaRRequest:
    """Tests for VaRRequest model."""
    
    def test_valid_request(self):
        """Test valid VaR request."""
        returns = [0.01, -0.02, 0.015, -0.01]
        request = VaRRequest(returns=returns, confidence_level=0.95, investment_value=10000)
        assert request.returns == returns
        assert request.confidence_level == 0.95
        assert request.investment_value == 10000
        
    def test_default_values(self):
        """Test default values."""
        returns = [0.01, -0.02]
        request = VaRRequest(returns=returns)
        assert request.confidence_level == 0.95
        assert request.investment_value == 1.0
        
    def test_missing_returns(self):
        """Test error when returns is missing."""
        with pytest.raises(ValidationError):
            VaRRequest(confidence_level=0.95)
            
    def test_invalid_returns_type(self):
        """Test error with invalid returns type."""
        with pytest.raises(ValidationError):
            VaRRequest(returns="invalid")
            
    def test_empty_returns_list(self):
        """Test with empty returns list."""
        request = VaRRequest(returns=[])
        assert request.returns == []


class TestPortfolioVaRRequest:
    """Tests for PortfolioVaRRequest model."""
    
    def test_valid_request(self):
        """Test valid portfolio VaR request."""
        request = PortfolioVaRRequest(
            tickers=["AAPL", "GOOGL"],
            weights=[0.6, 0.4],
            days=252,
            confidence_level=0.95,
            investment_value=100000,
            method="historical"
        )
        assert request.tickers == ["AAPL", "GOOGL"]
        assert request.weights == [0.6, 0.4]
        assert request.days == 252
        assert request.confidence_level == 0.95
        assert request.investment_value == 100000
        assert request.method == "historical"
        
    def test_default_values(self):
        """Test default values."""
        request = PortfolioVaRRequest(
            tickers=["AAPL"],
            weights=[1.0]
        )
        assert request.days == 252
        assert request.confidence_level == 0.95
        assert request.investment_value == 100000.0
        assert request.method == "historical"
        
    def test_parametric_method(self):
        """Test with parametric method."""
        request = PortfolioVaRRequest(
            tickers=["AAPL", "GOOGL"],
            weights=[0.5, 0.5],
            method="parametric"
        )
        assert request.method == "parametric"
        
    def test_missing_tickers(self):
        """Test error when tickers is missing."""
        with pytest.raises(ValidationError):
            PortfolioVaRRequest(weights=[0.5, 0.5])
            
    def test_missing_weights(self):
        """Test error when weights is missing."""
        with pytest.raises(ValidationError):
            PortfolioVaRRequest(tickers=["AAPL", "GOOGL"])
            
    def test_invalid_tickers_type(self):
        """Test error with invalid tickers type."""
        with pytest.raises(ValidationError):
            PortfolioVaRRequest(tickers="AAPL", weights=[1.0])
            
    def test_invalid_weights_type(self):
        """Test error with invalid weights type."""
        with pytest.raises(ValidationError):
            PortfolioVaRRequest(tickers=["AAPL"], weights=0.5)
            
    def test_mismatched_lengths(self):
        """Test with mismatched tickers and weights lengths."""
        # Note: Pydantic won't catch this - it's validated in the API endpoint
        request = PortfolioVaRRequest(
            tickers=["AAPL", "GOOGL"],
            weights=[1.0]  # Length mismatch
        )
        # This will pass validation but should fail in the API
        assert len(request.tickers) != len(request.weights)
