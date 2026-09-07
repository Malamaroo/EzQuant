import pandas as pd
import numpy as np
returns = pd.read_csv('Data/Processed/full_price_history.csv')
def reduce_to_portfolio(returns, portfolio):
    #Reduce the stocks to just the user's portfolio
    portfolio['Value'] = portfolio['Value'].astype(float)
    portfolio_stocks = portfolio['Stock'].tolist()
    portfolio_stocks = ['Date'] + portfolio_stocks
    portfolio_returns = returns[portfolio_stocks]

    returns_change = portfolio_returns.drop(columns=['Date'])
    returns_change.insert(0, 'Date', portfolio_returns['Date'])
    returns_change = returns_change.iloc[1:]  # Remove the first row which will be NaN after pct_change

    return_list = []
    for return_index, return_row in returns_change.iterrows():
        weekly_value_i = 0
        for portfolio_index, portfolio_row in portfolio.iterrows():
            stock_i_value = portfolio_row['Weighting']
            stock_i = portfolio_row['Stock']
            stock_i_value = stock_i_value * return_row[stock_i]
            portfolio.loc[portfolio_index, 'Value'] = stock_i_value
            weekly_value_i = weekly_value_i + stock_i_value
        return_list.append(weekly_value_i)
    total_portfolio_returns = pd.DataFrame({'Date': returns_change['Date'], 'Portfolio_Return': return_list})
    total_portfolio_returns.to_csv(f'Data/Portfolio/portfolio_returns.csv', index=False)
    return total_portfolio_returns

def build_covariance_matrix(portfolio_returns, portfolio):
    remove_stocks = portfolio['Stock'].tolist()
    all_returns = pd.read_csv('Data/Processed/full_price_history.csv')
    portfolio_and_stocks = pd.merge(portfolio_returns, all_returns, on ='Date')
    portfolio_and_stocks = portfolio_and_stocks.drop(columns=['Date'])
    portfolio_and_stocks = portfolio_and_stocks.rename(columns={'Portfolio_Return': 'Portfolio'})
    portfolio_and_stocks = portfolio_and_stocks.drop(columns=remove_stocks)
    portfolio_and_stocks = portfolio_and_stocks.pct_change()
    covariance_matrix = portfolio_and_stocks.cov()
    covariance_matrix.to_csv('Data/Portfolio/covariance_matrix.csv')


def recommend_hedge():
    covariance_matrix = pd.read_csv('Data/Portfolio/covariance_matrix.csv', index_col =0, header=0)
    covariance_matrix = covariance_matrix.iloc[1:]
    print(covariance_matrix)
    cov_value_i = 1
    for cov_index, cov_row in covariance_matrix.iterrows():
        cov_value_o = cov_row['Portfolio']
        if cov_value_o < cov_value_i:
            stock_recommendation = cov_index
            cov_value_i = cov_value_o
    return stock_recommendation, cov_value_i

   
def main():
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv',index_col=None, header=0)
    returns = pd.read_csv('Data/Processed/full_price_history.csv')
    total_portfolio_returns = reduce_to_portfolio(returns, portfolio)
    build_covariance_matrix(total_portfolio_returns, portfolio)
    stock_recommendation, covariance_value = recommend_hedge()
    print(f"The best stock to hedge your portfolio is {stock_recommendation} with a covariance value of {covariance_value}")
main()