"""
Flask frontend for VaR simulation and stock analysis.
"""
import sys
sys.path.append('../')

import requests
import json

from flask import Flask, render_template, request

from src.metrics import historical_var, parametric_var


app = Flask(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

@app.route('/')
def index():
    """Home page with links to different analysis tools."""
    return render_template('index.html')

@app.route('/stock-analysis', methods=['GET', 'POST'])
def stock_analysis():
    """Stock analysis page with interactive chart."""
    if request.method == 'POST':
        try:
            ticker = request.form.get('ticker', '').strip().upper()
            days = request.form.get('days')
            end_date = request.form.get('end_date')

            # response = requests.post(
            #     f"{API_BASE_URL}/",
            #     headers={"Content-Type": "application/json"},
            #     data=json.dumps({
            #         "ticker": ticker,
            #         "days": days,
            #         "end_date": end_date if end_date else None
            #     })
            # )
            
            # if response.status_code == 200:
            #     return render_template(
            #         'stock_analysis.html',
            #         plot=response.json().get('html')
            #     )
            # else:
            #     error_msg = response.json().get('detail', 'Unknown error occurred')
            #     return render_template('stock_analysis.html', error=error_msg)
                

            
        except Exception as e:
            return render_template('stock_analysis.html', error=str(e))
    
    return render_template('stock_analysis.html')

@app.route('/var-analysis', methods=['GET'])
def var_analysis():
    """VaR analysis page for portfolio risk assessment."""
    return render_template('var_analysis.html')

@app.route('/var-analysis/single', methods=['POST'])
def var_analysis_single():
    """Handle single asset VaR calculation."""
    if request.method == 'POST':
        try:
            returns = request.form.get('returns')
            confidence_level = request.form.get('confidence_level')
            investment_value = request.form.get('investment_value')

            returns = returns.replace(' ', '').replace('\n', ',').replace('[', '').replace(']', '')
            returns = [float(r) for r in returns.split(',') if r.strip()]

            # response = requests.post(
            #     f"{API_BASE_URL}/var-simulation",
            #     headers={"Content-Type": "application/json"},
            #     data=data,
            #     json.dumps({
            #         "returns": returns,
            #         "confidence_level": confidence_level,
            #         "investment_value": investment_value,
            #     })
            # )
            
            # if response.status_code == 200:
            #     result = response.json()

            return render_template(
                'var_analysis.html',
                parametric_var=historical_var(
                    returns,
                    float(confidence_level),
                    float(investment_value)
                ),
                historical_var=parametric_var(
                    returns,
                    float(confidence_level),
                    float(investment_value)
                ),
                confidence_level=float(confidence_level),
            )
                
        except Exception as e:
            return render_template(
                'var_analysis.html', 
                error=str(e)
            )
    
    return render_template('var_analysis.html')


@app.route('/var-analysis/portfolio', methods=['POST'])
def var_analysis_portfolio():
    """Handle multi asset VaR calculation."""
    if request.method == 'POST':
        try:
            ticker = request.form.get('ticker')
            returns = request.form.get('returns')
            confidence_level = request.form.get('confidence_level')
            investment_value = request.form.get('investment_value')
            
            response = requests.post(
                f"{API_BASE_URL}/var-simulation-portfolio",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "tickers": [ticker],
                    "returns": returns,
                    "confidence_level": confidence_level,
                    "investment_value": investment_value,
                })
            )
            
            if response.status_code == 200:
                result = response.json()

                return render_template(
                    'var_analysis.html',
                    results=result,
                    confidence_level=confidence_level,
                )
                
        except Exception as e:
            return render_template(
                'var_analysis.html', 
                error=str(e)
            )
    
    return render_template('var_analysis.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)