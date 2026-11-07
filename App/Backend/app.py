from flask import Flask, jsonify, request, render_template
from pathlib import Path
import pandas as pd
from hedging import hedge

backend_dir = Path(__file__).parent
app_dir = backend_dir.parent
frontend_dir = app_dir / 'FrontEnd'
project_dir = app_dir.parent
portfolio_file = project_dir / 'Data' / 'Portfolio' / 'portfolio.csv'


app = Flask(
    __name__,
    template_folder= str(frontend_dir),
    static_folder= str(frontend_dir),
    static_url_path= '/static'
)
    

all_stocks = ['JNJ', 'JPM', 'PG', 'XOM',
                'NEE', 'CAT', 'LIN', 'PLD',
                'MCD','WMT','BA','UPS',
                'INTC','V','WM',
                ]

initial_capital = 1000000


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!', 'number': 42})


@app.route('/api/stocks')
def get_stocks():
    return jsonify({'stocks': all_stocks})
@app.route('/api/portfolio', methods=['POST'])
def save_portfolio():
    data = request.get_json()
    holdings = data['portfolio']
    
    if len(holdings) == 0:
        return jsonify({'error': 'Portfolio is empty'}), 400
    
    for holding in holdings:
        if holding['value'] < 5000:
            return jsonify({'error': f"Value for {holding['stock']} must be greater than $5000"}), 400
        
    total = sum(holding['value'] for holding in holdings)
    if total > initial_capital:
        return jsonify({'error': 'Total portfolio value exceeds initial capital'}), 400
        
    rows = []
    for holding in holdings:
        rows.append({
            'Stock': holding['stock'],
            'Weight': holding['value'] / total,
            'Value': holding['value']
            })
        
    portfolio_df = pd.DataFrame(rows)
    portfolio_df.to_csv(portfolio_file, index=False)
    return jsonify({'message': 'Portfolio saved!', 'cash_left': initial_capital - total})
@app.route('/api/portfolio/reset', methods=['POST'])
def reset_portfolio():
    empty_portfolio = pd.DataFrame(columns=['Stock', 'Weight', 'Value'])
    empty_portfolio.to_csv(portfolio_file, index=False)
    return jsonify({'message': 'Portfolio reset.'})

@app.route('/api/hedge')
def hedge_portfolio():
    stock, covariance = hedge()
    return jsonify({'stock_recommendation': stock, 'covariance_value': covariance})


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=8000, debug=True)
