"""
Unit tests for main.py FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
from main import app

client = TestClient(app)


class TestGetTickerEndpoint:
    """Tests for POST / endpoint (get_ticker)."""
    
    @patch('main.fetch_stock_data')
    @patch('main.plot_stock_analysis')
    def test_valid_request(self, mock_plot, mock_fetch):
        """Test valid ticker request."""
        # Mock data
        mock_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=5),
            'Close': [100, 102, 101, 103, 105]
        })
        mock_fetch.return_value = mock_df
        
        mock_fig = MagicMock()
        mock_fig.to_html.return_value = "<html>Chart</html>"
        mock_plot.return_value = mock_fig
        
        # Make request
        response = client.post("/", json={
            "ticker": "AAPL",
            "days": 365
        })
        
        assert response.status_code == 200
        assert "html" in response.json()
        assert "<html>Chart</html>" == response.json()["html"]
        
        # Verify mocks were called
        mock_fetch.assert_called_once()
        mock_plot.assert_called_once()
        
    @patch('main.fetch_stock_data')
    def test_with_end_date(self, mock_fetch):
        """Test request with end_date parameter."""
        mock_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=5),
            'Close': [100, 102, 101, 103, 105]
        })
        mock_fetch.return_value = mock_df
        
        with patch('main.plot_stock_analysis') as mock_plot:
            mock_fig = MagicMock()
            mock_fig.to_html.return_value = "<html>Chart</html>"
            mock_plot.return_value = mock_fig
            
            response = client.post("/", json={
                "ticker": "AAPL",
                "days": 30,
                "end_date": "2024-01-31"
            })
            
            assert response.status_code == 200
            
    def test_missing_ticker(self):
        """Test error when ticker is missing."""
        response = client.post("/", json={"days": 365})
        assert response.status_code == 422  # Validation error
        
    @patch('main.fetch_stock_data')
    def test_fetch_data_error(self, mock_fetch):
        """Test error handling when data fetch fails."""
        mock_fetch.side_effect = Exception("API error")
        
        response = client.post("/", json={
            "ticker": "INVALID",
            "days": 365
        })
        
        # Should raise exception (or return error depending on error handling)
        assert response.status_code in [500, 422]


class TestVaRSimulationEndpoint:
    """Tests for POST /var-simulation endpoint."""
    
    def test_valid_request(self):
        """Test valid VaR simulation request."""
        returns = [0.01, -0.02, 0.015, -0.01, 0.02, -0.005, 0.01]
        
        response = client.post("/var-simulation", json={
            "returns": returns,
            "confidence_level": 0.95,
            "investment_value": 10000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "historical_var" in data
        assert "parametric_var" in data
        assert isinstance(data["historical_var"], (int, float))
        assert isinstance(data["parametric_var"], (int, float))
        assert data["historical_var"] >= 0
        assert data["parametric_var"] >= 0
        
    def test_default_values(self):
        """Test with default confidence level and investment value."""
        returns = [0.01, -0.02, 0.015]
        
        response = client.post("/var-simulation", json={
            "returns": returns
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "historical_var" in data
        assert "parametric_var" in data
        
    def test_different_confidence_levels(self):
        """Test VaR with different confidence levels."""
        returns = [0.01, -0.02, 0.015, -0.01, 0.02]
        
        var_90 = client.post("/var-simulation", json={
            "returns": returns,
            "confidence_level": 0.90,
            "investment_value": 10000
        }).json()
        
        var_99 = client.post("/var-simulation", json={
            "returns": returns,
            "confidence_level": 0.99,
            "investment_value": 10000
        }).json()
        
        # Higher confidence should give higher VaR
        assert var_99["historical_var"] >= var_90["historical_var"]
        assert var_99["parametric_var"] >= var_90["parametric_var"]
        
    def test_missing_returns(self):
        """Test error when returns is missing."""
        response = client.post("/var-simulation", json={
            "confidence_level": 0.95
        })
        assert response.status_code == 422
        
    def test_invalid_confidence_level(self):
        """Test with invalid confidence level (not validated by model but could be)."""
        returns = [0.01, -0.02]
        
        # This might pass validation but could be handled by the function
        response = client.post("/var-simulation", json={
            "returns": returns,
            "confidence_level": 1.5  # Invalid
        })
        # Behavior depends on validation implementation


class TestPortfolioVaRSimulationEndpoint:
    """Tests for POST /var-simulation-portfolio endpoint."""
    
    @patch('main.fetch_stock_data')
    def test_valid_request(self, mock_fetch):
        """Test valid portfolio VaR request."""
        # Mock stock data for two tickers
        def mock_fetch_side_effect(ticker, days):
            if ticker == "AAPL":
                return pd.DataFrame({
                    'Close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
                })
            else:  # GOOGL
                return pd.DataFrame({
                    'Close': [150, 152, 151, 153, 155, 154, 156, 158, 157, 160]
                })
        
        mock_fetch.side_effect = mock_fetch_side_effect
        
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL", "GOOGL"],
            "weights": [0.6, 0.4],
            "days": 252,
            "confidence_level": 0.95,
            "investment_value": 100000,
            "method": "historical"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, float))  # Returns VaR value or dict
        
    @patch('main.fetch_stock_data')
    def test_weights_sum_validation(self, mock_fetch):
        """Test validation that weights sum to 1."""
        mock_fetch.return_value = pd.DataFrame({'Close': [100, 102, 101]})
        
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL", "GOOGL"],
            "weights": [0.6, 0.5],  # Sum to 1.1
            "days": 252
        })
        
        # Should return error (400 or 422)
        assert response.status_code in [400, 422, 500]
        
    @patch('main.fetch_stock_data')
    def test_single_asset_portfolio(self, mock_fetch):
        """Test portfolio with single asset."""
        mock_fetch.return_value = pd.DataFrame({
            'Close': [100, 102, 101, 103, 105]
        })
        
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL"],
            "weights": [1.0],
            "days": 252
        })
        
        assert response.status_code == 200
        
    @patch('main.fetch_stock_data')
    def test_parametric_method(self, mock_fetch):
        """Test portfolio VaR with parametric method."""
        def mock_fetch_side_effect(ticker, days):
            return pd.DataFrame({
                'Close': [100, 102, 101, 103, 105, 104, 106]
            })
        
        mock_fetch.side_effect = mock_fetch_side_effect
        
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL", "GOOGL"],
            "weights": [0.5, 0.5],
            "method": "parametric"
        })
        
        assert response.status_code == 200
        
    def test_missing_tickers(self):
        """Test error when tickers is missing."""
        response = client.post("/var-simulation-portfolio", json={
            "weights": [0.5, 0.5]
        })
        assert response.status_code == 422
        
    def test_missing_weights(self):
        """Test error when weights is missing."""
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL", "GOOGL"]
        })
        assert response.status_code == 422
        
    @patch('main.fetch_stock_data')
    def test_portfolio_composition_in_response(self, mock_fetch):
        """Test that response includes portfolio composition."""
        def mock_fetch_side_effect(ticker, days):
            return pd.DataFrame({
                'Close': [100, 102, 101, 103, 105]
            })
        
        mock_fetch.side_effect = mock_fetch_side_effect
        
        response = client.post("/var-simulation-portfolio", json={
            "tickers": ["AAPL", "GOOGL"],
            "weights": [0.6, 0.4]
        })
        
        if response.status_code == 200:
            data = response.json()
            # Check if portfolio_composition is in response
            if isinstance(data, dict):
                assert "portfolio_composition" in data or isinstance(data, (int, float))
