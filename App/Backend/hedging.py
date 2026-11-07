import pandas as pd
import numpy as np
def hedge():
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv',index_col=None, header=0) #read in list of stocks and their weights in portfolio (all data is saved as CSVs to be easily accessed, readable, and straightforward to call later.)
    returns = pd.read_csv('Data/Processed/total_backtest_percentage_returns.csv') #read in list of percentage changes for every day.
    portfolio_returns = reduce_to_portfolio(returns, portfolio) #reduce stock to just the stocks the user has decided for their portfolio.
    build_portfolio_cov_matrix(portfolio_returns, portfolio) #build cov matrix of just portfolio stocks. 
    total_portfolio_returns = calculate_total_portfolio_returns(portfolio_returns, portfolio) #calculate the total returns of the user's portfolio, based on the percentage change of each stock in the portfolio and the weighting of each stock in the portfolio.
    covariance_matrix = build_adapted_covariance_matrix(total_portfolio_returns, portfolio) #build 
    stock_recommendation, covariance_value = recommend_hedge(covariance_matrix) #recommend the best stock to hedge the user's portfolio based on the covariance matrix of all stocks and the user's portfolio.
    return stock_recommendation, covariance_value

def reduce_to_portfolio(returns, portfolio): #reduce stock to just the stocks the user has decided for their portfolio.
    portfolio['Value'] = portfolio['Value'].astype(float) #ensure that the value column (of how much each stock is worth in the portfolio) is a float.
    portfolio_stocks = portfolio['Stock'].tolist() #create a list of the names of each stock
    portfolio_stocks = ['Date'] + portfolio_stocks #add 'date' with the list of stocks, so returns can be reduced to required stocks + portfolio stocks.
    portfolio_returns = returns[portfolio_stocks] #reduce the returns df of all stocks to just the stocks in the portfolio + date
    return portfolio_returns


def build_portfolio_cov_matrix(returns, portfolio):  #function designed to create a covariance matrix of all stocks included in the user's portfolio. This is then used for optimisation.
    returns_change = returns.drop(columns=['Date']) #remove the date data, so covariance (on lists of floats rather than datettime) can be calculated for each stock in the portfolio.
    returns_change.cov().to_csv(f'Data/Portfolio/covariance_matrix.csv', index=True) #calculate the cov matrix of just included portfolio and then save it as a CSV for later use.
    print(returns_change.cov())
    returns_change.insert(0, 'Date', returns['Date']) #re-insert the date column, so returns can be calculated for each week in the portfolio.
    print(returns_change)
    

def calculate_total_portfolio_returns(returns_change, portfolio): #function designed to calculate the total returns of the user's portfolio, based on the percentage change of each stock in the portfolio and the weighting of each stock in the portfolio.
    return_list = []
    for return_index, return_row in returns_change.iterrows():
        weekly_value_i = 0
        for portfolio_index, portfolio_row in portfolio.iterrows():
            stock_i_value = portfolio_row['Weight']
            stock_i = portfolio_row['Stock']
            stock_i_value = stock_i_value * return_row[stock_i]
            portfolio.loc[portfolio_index, 'Value'] = stock_i_value
            weekly_value_i = weekly_value_i + stock_i_value
        return_list.append(weekly_value_i)
    total_portfolio_returns = pd.DataFrame({'Date': returns_change['Date'], 'Portfolio_Return': return_list})
    total_portfolio_returns.to_csv(f'Data/Portfolio/portfolio_returns.csv', index=False)
    print(total_portfolio_returns)
    return total_portfolio_returns



def build_adapted_covariance_matrix(portfolio_returns, portfolio):
    remove_stocks = portfolio['Stock'].tolist()

    all_returns = pd.read_csv('Data/Processed/full_price_history.csv', header=0, index_col=None)
    all_returns_refined = all_returns.drop(columns=['Date'])
    all_returns_refined = all_returns_refined.pct_change()
    all_returns_refined.insert(0, 'Date', all_returns['Date'])
    all_returns_refined = all_returns_refined.iloc[1:].reset_index(drop=True)
    all_returns_refined['Date'] = pd.to_datetime(all_returns_refined['Date'], utc=True).dt.date  ###ensuring that date formats are the same for both dataframes

    portfolio_returns = portfolio_returns.drop(columns=['Date']) ### The following script was designed because of restrictive CPU load times which limits how data can be transferrred and therefore it leads to nothing being visible.
    print(f"Portfolio Returns:\n{portfolio_returns}")
    merged_returns = pd.concat([all_returns_refined, portfolio_returns], axis=1)
    merged_returns = merged_returns.drop(columns=['Date'])
    merged_returns = merged_returns.rename(columns={'Portfolio_Return': 'Portfolio'})
    merged_returns = merged_returns.drop(columns=remove_stocks)
    covariance_matrix = merged_returns.cov()
    covariance_matrix.to_csv('Data/Portfolio/adapted_covariance_matrix.csv')
    return covariance_matrix


def recommend_hedge(covariance_matrix):
    print(f"Covariance Matrix:\n{covariance_matrix}")
    covariance_matrix = covariance_matrix.drop(index='Portfolio')
    print(f"Covariance Matrix (without Portfolio row):\n{covariance_matrix}")
    cov_value_i = 1
    for cov_index, cov_row in covariance_matrix.iterrows():
        cov_value_o = cov_row['Portfolio']
        if cov_value_o < cov_value_i:
            stock_recommendation = cov_index
            cov_value_i = cov_value_o
    return stock_recommendation, cov_value_i

   
   
   
def main():
    stock_recommendation, covariance_value = hedge()
    print(f"The best stock to hedge your portfolio is {stock_recommendation} with a covariance value of {covariance_value}")
   
  
if __name__ == '__main__':
    main()