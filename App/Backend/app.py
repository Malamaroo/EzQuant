"""
This is the flask server that connects the frontend to the rest of the backend (hedging.py, optimiser.py and backtest.py).
Each route below takes a request from the frontend, checks it, calls the right backend file, and sends the result back as json.

AI DISCLOSURE: any block marked with "#AI WRITTEN" was written by AI (Claude), and everything inside it should be treated as AI generated.
Anything not marked (the imports, the file paths, the flask setup, all_stocks, initial_capital and the three simple starter routes) is my own work.
Nevertheless, I believe you should consider the frontend to be AI-created, and I dont personally claim it as my own work. The sole reason I utilised 
AI for the frontend was to just have a shell of the backend formula and structure that I had so dilligently created.
"""
from flask import Flask, jsonify, request, render_template
from pathlib import Path
import pandas as pd


from hedging import hedge
from optimiser import run_optimisation
from backtest import run_backtest


backend_dir = Path(__file__).parent #the folder this file is in
app_dir = backend_dir.parent #go up one folder to the App folder
frontend_dir = app_dir / 'FrontEnd' #the frontend folder, holds index.html, the css and the js
project_dir = app_dir.parent #go up again to the main project folder, so the Data folder can be reached
portfolio_file = project_dir / 'Data' / 'Portfolio' / 'portfolio.csv' #where the user's saved portfolio lives
price_history_file = project_dir / 'Data' / 'Processed' / 'full_price_history.csv' #the full weekly price history of every stock


app = Flask(
    __name__,
    template_folder= str(frontend_dir), #flask looks for index.html in the frontend folder
    static_folder= str(frontend_dir), #and the css/js are served from there too
    static_url_path= '/static'
)


all_stocks = ['JNJ', 'JPM', 'PG', 'XOM',
                'NEE', 'CAT', 'LIN', 'PLD',
                'MCD','WMT','BA','UPS',
                'INTC','V','WM',
                ] #every stock the user is allowed to pick from

initial_capital = 1000000 #how much money the user starts with ($1,000,000)

#AI WRITTEN: get_data_date_range (the whole function)
def get_data_date_range(): #finds the first and last date in the price history, so the backtest knows which dates are allowed.
    dates = pd.read_csv(price_history_file, usecols=['Date'])['Date'] #only read the date column, as the rest is not needed here
    dates = pd.to_datetime(dates, utc=True) #convert the text into actual dates
    return dates.min().strftime('%Y-%m-%d'), dates.max().strftime('%Y-%m-%d') #earliest and latest date, as text

#AI WRITTEN: read_portfolio (the whole function)
def read_portfolio(): #loads the saved portfolio csv as a dataframe, used by several routes below.
    # No file, or an empty file, just means "no portfolio yet"
    if not portfolio_file.exists() or portfolio_file.stat().st_size == 0:
        return pd.DataFrame(columns=['Stock', 'Weight', 'Value']) #return an empty portfolio so the other routes don't crash
    return pd.read_csv(portfolio_file)

@app.route('/')
def index():
    return render_template('index.html') #show the main page

#The following part's javascript and html reference were dismantled, but it was purely for my own educational purposes.
@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!', 'number': 42}) #just a test route, to check the frontend can talk to the backend


@app.route('/api/stocks')
def get_stocks():
    return jsonify({'stocks': all_stocks}) #send the frontend the list of stocks to choose from

#AI WRITTEN: save_portfolio (the whole route, including the validation and the weight calculation)
@app.route('/api/portfolio', methods=['POST'])
def save_portfolio(): #takes the stocks and dollar amounts the user chose, checks them, and saves them to portfolio.csv
    data = request.get_json()
    holdings = data['portfolio']

    if len(holdings) == 0:
        return jsonify({'error': 'Portfolio is empty'}), 400 #can't save nothing

    for holding in holdings:
        if holding['value'] < 5000:
            return jsonify({'error': f"Value for {holding['stock']} must be greater than $5000"}), 400 #every stock needs a minimum investment

    total = sum(holding['value'] for holding in holdings) #add up everything the user wants to invest
    if total > initial_capital:
        return jsonify({'error': 'Total portfolio value exceeds initial capital'}), 400 #they can't spend more than they have

    rows = []
    for holding in holdings:
        rows.append({
            'Stock': holding['stock'],
            'Weight': holding['value'] / total, #the fraction of the invested money that is in this stock
            'Value': holding['value']
            })

    portfolio_df = pd.DataFrame(rows)
    portfolio_df.to_csv(portfolio_file, index=False) #save it so the other files (hedging, optimiser, backtest) can load it
    return jsonify({'message': 'Portfolio saved!', 'cash_left': initial_capital - total})

#AI WRITTEN: reset_portfolio (the whole route)
@app.route('/api/portfolio/reset', methods=['POST'])
def reset_portfolio(): #wipes the saved portfolio by overwriting it with an empty one
    empty_portfolio = pd.DataFrame(columns=['Stock', 'Weight', 'Value'])
    empty_portfolio.to_csv(portfolio_file, index=False)
    return jsonify({'message': 'Portfolio reset.'})

#AI WRITTEN: current_portfolio (the whole route)
@app.route('/api/portfolio/current')
def current_portfolio(): #sends the frontend the saved portfolio, how much is invested, and how much cash is left
    portfolio = read_portfolio()
    invested = float(portfolio['Value'].sum()) if not portfolio.empty else 0.0
    return jsonify({
        'holdings': portfolio.to_dict(orient='records'),
        'invested': invested,
        'cash_left': initial_capital - invested,
    })

@app.route('/api/hedge')
def hedge_portfolio():
    stock, covariance = hedge() #hedge() is in hedging.py, it finds the stock with the most negative covariance to the portfolio
    return jsonify({'stock_recommendation': stock, 'covariance_value': covariance})

#AI WRITTEN: optimise_portfolio (the whole route, including all of the validation and error messages)
@app.route('/api/optimise', methods=['POST'])
def optimise_portfolio(): #re-balances the portfolio to the best return for the yearly risk the user typed in
    yearly_risk = request.json.get('yearly_risk')



    portfolio = read_portfolio()
    if len(portfolio) < 2:
        return jsonify({'error': 'Portfolio must contain at least 2 stocks to optimise.'}), 400 #there is nothing to rebalance with only one stock
    if yearly_risk is None or yearly_risk <= 0:
        return jsonify({'error': 'Please provide a valid yearly risk value greater than 0.'}), 400
    new_portfolio = run_optimisation(yearly_risk) #run_optimisation() is in optimiser.py
    if new_portfolio is None:
        return jsonify({'error': 'Optimization failed. No portfolio can reach a risk that low. Please input a higher value'}), 500 #the optimiser found no solution


    return jsonify({'message': 'Portfolio optimised!', 'new_portfolio': new_portfolio.to_dict(orient='records')})

#AI WRITTEN: backtest_portfolio (the whole route, including the date checks)
@app.route('/api/backtest', methods=['POST'])
def backtest_portfolio(): #checks the dates the user chose, then runs the portfolio over that period of history
    data = request.get_json()
    start_date = data['start_date']
    end_date = data['end_date']
    min_date, max_date = get_data_date_range()

    if not start_date or not end_date:
        return jsonify({'error': 'Please choose a start and end date.'}), 400
    if (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days < 14:
        return jsonify({'error': 'The end date must be at least 2 weeks after the start date.'}), 400 #the data is weekly, so less than 2 weeks gives no returns to work with

    if start_date < min_date or end_date > max_date:
        return jsonify({'error': f'Please choose dates between {min_date} and {max_date}.'}), 400 #can't backtest on data we don't have

    portfolio = read_portfolio()
    if portfolio.empty:
        return jsonify({'error': 'Your portfolio is empty. Save a portfolio first.'}), 400

    return jsonify(run_backtest(start_date, end_date)) #run_backtest() is in backtest.py

#AI WRITTEN: backtest_date_range (the whole route)
@app.route('/api/backtest/date-range')
def backtest_date_range(): #tells the frontend the earliest and latest dates the user can pick
    first_date, last_date = get_data_date_range()
    return jsonify({'first_date': first_date, 'last_date': last_date})






if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=8000, debug=True) #only runs the server when this file is run directly
