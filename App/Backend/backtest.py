import pandas as pd
import numpy as np

def main():
    returns = pd.read_csv('EzQuant/Data/Processed/full_price_history.csv')
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize()
    player_portfolio_backtest(returns)



def player_portfolio_backtest(returns):
    start_date, end_date = collect_dates()
    returns = returns
    backtest_static(start_date, end_date, returns, initial_capital=100000)



def collect_dates():
    print("Please write in yyyy-mm-dd format!")
    start_date = input("Please enter the start date for the backtest: ")
    if start_date == "m":
        start_date = "2020-01-01"  # Set a default start date
    end_date = input("Please enter the end date for the backtest: ")
    if end_date == "m":
        end_date = "2023-01-01"  # Set a default end date
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
    range_returns = returns.loc[(returns['Date'] >= pd.to_datetime(start_date)) & (returns['Date'] <= pd.to_datetime(end_date))]
    range_returns.to_csv('EzQuant/Data/Processed/range_returns.csv', index=False)
    return

    
def backtest_strategy_flexible(data, strategy_func, initial_capital=10000):
    return

main()

