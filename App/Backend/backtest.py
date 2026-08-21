import pandas as pd
import numpy as np

def main():
    returns = pd.read_csv('EzQuant/Data/Processed/full_price_history.csv')
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize()
    total_return, final_portfolio_value, years = player_portfolio_backtest(returns)
    print(f'The final portfolio value is: ${final_portfolio_value:,.2f}')
    print(f'The total return of the portfolio over the backtest period was: {total_return:.2%}')
    print(f'The backtest period was: {years:.2f} years')   
    print(f'The average annual return of the portfolio over the backtest period was: {(total_return/years):.2%}')

def player_portfolio_backtest(returns):
    start_date, end_date = collect_dates()
    years = ((pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25)
    returns = returns
    total_return, final_portfolio_value = backtest_static(start_date, end_date, returns, initial_capital=1000000)
    return total_return, final_portfolio_value, years


def collect_dates():
    print("Please write in yyyy-mm-dd format!")
    start_date = input("Please enter the start date for the backtest: ")
    if start_date == "m":
        start_date = "2016-01-01"  # Set a default start date
    end_date = input("Please enter the end date for the backtest: ")
    if end_date == "m":
        end_date = "2023-06-08"  # Set a default end date
    return start_date, end_date



def backtest_static(start_date, end_date,  returns, initial_capital=0):
    """
    Backtest a portfolio of trading strategies.

    Parameters:
    - start_date: The start date for the backtest period.
    - end_date: The end date for the backtest period.
    - portfolio: A dataframe where each column is a time series of a stock's returns
    - initial_capital: The starting capital for the backtest.

    Returns:
    -A DataFrame with the backtest results of the portfolio over time (Percentage change)
    -The total return of the portfolio over the backtest period.

    How:
    1. for every week in the backtest period, calculate the returns of each stock multipled by the weight of that stock in the portfolio.
    2. Sum the returns of all stocks to get the total return of the portfolio for that week.
    3. Repeat this process for every week in the backtest period.
    4. Calculate the cumulative returns of the portfolio over time.
    """

    #Reduce the stocks to just the user's portfolio
    portfolio = pd.read_csv('EzQuant/Data/Portfolio/portfolio.csv',index_col=None, header=0)
    print(portfolio)
    portfolio_stocks = portfolio['Stock'].tolist()
    portfolio_stocks = ['Date'] + portfolio_stocks
   





    #Calculate the returns of all stocks over the portfolio period
    portfolio_returns = returns[portfolio_stocks]
    print(portfolio_returns)
    range_returns = portfolio_returns.loc[(returns['Date'] >= pd.to_datetime(start_date)) & (returns['Date'] <= pd.to_datetime(end_date))]
    returns_change = range_returns.drop(columns=['Date'])
    returns_change = returns_change.pct_change()
    returns_change.insert(0, 'Date', range_returns['Date'])
    returns_change = returns_change.iloc[1:]  # Remove the first row which will be NaN after pct_change
    returns_change.to_csv(f'EzQuant/Data/Processed/backtest_percentage_returns.csv', index=False)

    #Calculate average weekly returns of portfolio for each week
    total_return = 0
    total_portfolio_returns = pd.Series(dtype='float64')
    return_list = []
    for return_index, return_row in returns_change.iterrows():
        weekly_return = 0
        for portfolio_index, portfolio_row in portfolio.iterrows():
            weight_i = portfolio_row['Weighting']
            stock_i = portfolio_row['Stock']
            weekly_return = weekly_return + (weight_i * return_row[stock_i])
        total_return = total_return + weekly_return
        return_list.append(weekly_return)
        print(weekly_return)
    total_portfolio_returns = pd.DataFrame({'Date': returns_change['Date'], 'Total_Return': return_list})
    total_portfolio_returns.to_csv(f'EzQuant/Data/Processed/backtest_total_returns.csv', index=False)
    final_portfolio_value = initial_capital * (1 + total_return)
    return total_return, final_portfolio_value



def backtest_strategy_flexible(data, strategy_func, initial_capital=10000):
    return

main()

