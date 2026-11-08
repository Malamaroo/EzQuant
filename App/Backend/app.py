from flask import Flask, jsonify, request, render_template
from pathlib import Path
import pandas as pd


from hedging import hedge
from optimiser import run_optimisation
from backtest import run_backtest


backend_dir = Path(__file__).parent
app_dir = backend_dir.parent
frontend_dir = app_dir / 'FrontEnd'
project_dir = app_dir.parent
portfolio_file = project_dir / 'Data' / 'Portfolio' / 'portfolio.csv'
price_history_file = project_dir / 'Data' / 'Processed' / 'full_price_history.csv'


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

def get_data_date_range():
    dates = pd.read_csv(price_history_file, usecols=['Date'])['Date']
    dates = pd.to_datetime(dates, utc=True)
    return dates.min().strftime('%Y-%m-%d'), dates.max().strftime('%Y-%m-%d')


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


@app.route('/api/optimise', methods=['POST'])
def optimise_portfolio():
    yearly_risk = request.json.get('yearly_risk')
    
    
    #crucial that portfolio has already been hedged, as this is what builds the cov matrix
    portolio = pd.read_csv(portfolio_file)
    cov_matrix = pd.read_csv(project_dir / 'Data' / 'Portfolio' / 'covariance_matrix.csv', index_col=0)
    if sorted(portolio['Stock'].tolist()) != sorted(cov_matrix.columns.tolist()):
        return jsonify({'error': 'Please hedge your portfolio before optimising'}), 400
    
    new_portfolio = run_optimisation(yearly_risk)
    if new_portfolio is None:
        return jsonify({'error': 'Optimization failed. No portfolio can reach a risk that low. Please input a higher value'}), 500
    
    
    return jsonify({'message': 'Portfolio optimised!', 'new_portfolio': new_portfolio.to_dict(orient='records')})

@app.route('/api/backtest', methods=['POST'])
def backtest_portfolio():
    data = request.get_json()
    start_date = data['start_date']
    end_date = data['end_date']
    min_date, max_date = get_data_date_range()

    if not start_date or not end_date:
        return jsonify({'error': 'Please choose a start and end date.'}), 400
    if (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days < 14:
        return jsonify({'error': 'The end date must be at least 2 weeks after the start date.'}), 400
    
    if start_date < min_date or end_date > max_date:
        return jsonify({'error': f'Please choose dates between {min_date} and {max_date}.'}), 400
   
    portfolio = pd.read_csv(portfolio_file)
    if portfolio.empty:
        return jsonify({'error': 'Your portfolio is empty. Save a portfolio first.'}), 400

    return jsonify(run_backtest(start_date, end_date))


@app.route('/api/backtest/date-range')
def backtest_date_range():
    first_date, last_date = get_data_date_range()
    return jsonify({'first_date': first_date, 'last_date': last_date})






if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=8000, debug=True)
