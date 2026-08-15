import yfinance as yf
import pandas as pd

def main():
    initial_stock_data()
    get_stock_data()

def initial_stock_data():
    aapl = yf.Ticker("AAPL")  # Get the stock data for Apple

    aapl_history = aapl.history(period="10y", interval="1wk")  # Get total historical data 
    aapl_p = aapl_history[['Close']].reset_index()  # Get the closing prices

    aapl_e_history = aapl.get_earnings_dates(limit=100)
    aapl_e= aapl_e_history[['Reported EPS']].reset_index()  # Get the earnings dates
    aapl_e = aapl_e.rename(columns={'Earnings Date': 'Date'})
    
    aapl_p = aapl_p.sort_values('Date')
    aapl_e = aapl_e.sort_values('Date')
        
    aapl_ep = pd.merge_asof(aapl_p, aapl_p, on='Date', direction='backward')  # Merge earnings dates with closing prices
        
    aapl_ep.to_csv(f'Data/Raw/aapl_data.csv', index=False)  # Save the merged data to a CSV file

    aapl_p = aapl_p.rename(columns={'Close': 'AAPL'})

    pricedf = pd.DataFrame(aapl_p)

def get_stock_data():
    tickers = ['JNJ', 'JPM', 'PG', 'XOM', 'NEE', 'CAT', 'LIN', 'PLD', 'MCD']  # List of all stock tickers the user can choose from
    for ticker in tickers:
        stock_i = yf.Ticker(ticker)
        
        
        stock_i_history = stock_i.history(period="10y", interval="1wk")  # Get total historical data 
        stock_i_p = stock_i_history[['Close']].reset_index()  # Get the closing prices

        stock_i_e_history = stock_i.get_earnings_dates(limit=100)
        stock_i_e = stock_i_e_history[['Reported EPS']].reset_index()  # Get the earnings dates
        stock_i_e = stock_i_e.rename(columns={'Earnings Date': 'Date'})
        
        
        stock_i_p = stock_i_p.sort_values('Date')
        stock_i_e = stock_i_e.sort_values('Date')
        
        stock_i_ep = pd.merge_asof(stock_i_p, stock_i_e, on='Date', direction='backward')  # Merge earnings dates with closing prices
        
        stock_i_ep.to_csv(f'Data/Raw/{ticker}_data.csv', index=False)  # Save the merged data to a CSV file

main()