import yfinance as yf
import pandas as pd

tickers = ['AAPL', 'JNJ', 'JPM', 'PG', 'XOM', 'NEE', 'CAT', 'LIN', 'PLD', 'MCD']  # List of all stock tickers the user can choose from
for ticker in tickers:
    stock_i = yf.Ticker(ticker)
    
    
    stock_i_history = stock_i.history(period="10y", interval="1wk")  # Get historical data for the past 10 years
    stock_i_p = stock_i_history[['Close']].reset_index()  # Get the closing prices for the past 10 years

    stock_i_e_history = stock_i.get_earnings_dates(limit=100)
    stock_i_e = stock_i_e_history[['Reported EPS']].reset_index()  # Get the earnings dates for the past 10 years
    stock_i_e = stock_i_e.rename(columns={'Earnings Date': 'Date'})
    
    
    stock_i_p = stock_i_p.sort_values('Date')
    stock_i_e = stock_i_e.sort_values('Date')
    
    stock_i_ep = pd.merge_asof(stock_i_p, stock_i_e, on='Date', direction='backward')  # Merge earnings dates with closing prices
    
    stock_i_ep.to_csv(f'Data/Raw/{ticker}_data.csv', index=False)  # Save the merged data to a CSV file