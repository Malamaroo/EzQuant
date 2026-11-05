import yfinance as yf
import pandas as pd


###This should be cleaned up, to not have the intial pull. Perhaps make it so they are all created as the list then combined into it.


def main():
    price_df, pe_ratio_df = initial_stock_data()
    price_df = get_stock_data(price_df, pe_ratio_df)
    calculate_covariance_matrix(price_df)
def initial_stock_data():
    aapl = yf.Ticker("AAPL")  # Get the stock data for Apple

    aapl_history = aapl.history(period="20y", interval="1wk")  # Get total historical data 
    aapl_p = aapl_history[['Close']].reset_index()  # Get the closing prices

    aapl_e_history = aapl.get_earnings_dates(limit=100)
    aapl_e= aapl_e_history[['Reported EPS']].reset_index()  # Get the earnings dates
    aapl_e = aapl_e.rename(columns={'Earnings Date': 'Date'})
    
    aapl_p = aapl_p.sort_values('Date')
    aapl_e = aapl_e.sort_values('Date')
    aapl_p['Date'] = aapl_p['Date'].dt.as_unit('us')
    aapl_e['Date'] = aapl_e['Date'].dt.as_unit('us')
        
    aapl_ep = pd.merge_asof(aapl_p, aapl_e, on='Date', direction='backward')  # Merge earnings dates with closing prices
    aapl_ep.to_csv(f'Data/Raw/aapl_data.csv', index=False)  # Save the merged data to a CSV file

    aapl_p = aapl_p.rename(columns={'Close': 'AAPL'})
    aapl_e = aapl_e.rename(columns={'Reported EPS': 'AAPL'})


    price_df = pd.DataFrame(aapl_p)
    pe_ratio_df = pe_ratio(aapl_ep, ticker='AAPL')  # Calculate the PE ratio for Apple and return it as a dataframe

    return price_df, pe_ratio_df

def get_stock_data(price_df, pe_ratio_df):
    tickers = ['JNJ', 'JPM', 'PG', 'XOM',
                'NEE', 'CAT', 'LIN', 'PLD',
                'MCD','WMT','BA','UPS',
                'INTC','V','WM',
                ]  # List of all stock tickers the user can choose from

    for ticker in tickers:
        stock_i = yf.Ticker(ticker)
        
        #get historical price
        stock_i_history = stock_i.history(period="20y", interval="1wk")  # Get total historical data 
        stock_i_p = stock_i_history[['Close']].reset_index()  # Get the closing prices
        stock_i_p_df = pd.DataFrame(stock_i_p)

        stock_i_e_history = stock_i.get_earnings_dates(limit=100)
        stock_i_e = stock_i_e_history[['Reported EPS']].reset_index()  # Get the earnings dates
        stock_i_e = stock_i_e.rename(columns={'Earnings Date': 'Date'})
        
        
        stock_i_p = stock_i_p.sort_values('Date')
        stock_i_e = stock_i_e.sort_values('Date')

        stock_i_p['Date'] = stock_i_p['Date'].dt.as_unit('us')
        stock_i_e['Date'] = stock_i_e['Date'].dt.as_unit('us')
        print(stock_i_e)

        stock_i_ep = pd.merge_asof(stock_i_p, stock_i_e, on='Date', direction='backward')  # Merge earnings dates with closing prices

        #create comprehensive price history dataframe
        stock_i_ep.to_csv(f'Data/Raw/{ticker}_data.csv', index=False)  # Save the merged data to a CSV file
        stock_i_p = stock_i_p.rename(columns={'Close': ticker}) # rename the closing price column to the stock ticker
        stock_i_p_df = pd.DataFrame(stock_i_p) # turn closing price column into a dataframe
        price_df = pd.merge(price_df, stock_i_p_df, on='Date')  #append price data to the main dataframe
        #create comprehensive p/e ratio dataframe
        stock_i_pe_ratio = pe_ratio(stock_i_ep, ticker=ticker)  # Calculate the PE ratio for the stock and return it as a dataframe
        pe_ratio_df = pd.merge(pe_ratio_df, stock_i_pe_ratio, on='Date')


    price_df.to_csv(f'Data/Processed/full_price_history.csv', index=False)  # save the full price history to a CSV file
    pe_ratio_df.to_csv(f'Data/Processed/full_pe_ratios.csv', index=False)  # save the full p/e ratios to a CSV file
    return price_df

def pe_ratio(stock_e_and_p, ticker):
    for ratio_index, ratio_row in stock_e_and_p.iterrows():
        if ratio_row['Reported EPS'] == 0:
            stock_e_and_p.loc[ratio_index, 'PE Ratio'] = 0
        else:
            stock_e_and_p.loc[ratio_index, 'PE Ratio'] = ratio_row['Close'] / ratio_row['Reported EPS']
    stock_e_and_p = stock_e_and_p.rename(columns={'PE Ratio': ticker})
    stock_e_and_p = stock_e_and_p.drop(columns=['Close', 'Reported EPS'])
    return stock_e_and_p

def calculate_covariance_matrix(price_df):
    price_df = price_df.drop(columns="Date")
    price_df = price_df.pct_change()
    covariance_matrix = price_df.cov()
    covariance_matrix.to_csv(f'Data/Processed/full_covariance_matrix.csv')
main()