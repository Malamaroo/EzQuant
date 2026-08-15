import pandas as pd

def backtest_portfolio(start_date, end_date, portfolio, returns, initial_capital=10000):
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
    backtest_range = pd.date_range(start=start_date, end=end_date, freq='W')






def backtest_strategy_flexible(data, strategy_func, initial_capital=10000):