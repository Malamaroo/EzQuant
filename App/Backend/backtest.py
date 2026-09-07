import pandas as pd
import numpy as np
import statistics as stat

def main():
    returns = pd.read_csv('EzQuant/Data/Processed/full_price_history.csv')
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize()
    total_return, final_portfolio_value, Portfolio_SharpeRatio, years = player_portfolio_backtest(returns)
    print(f'The final portfolio value is: ${final_portfolio_value:,.2f}')
    print(f'The total return of the portfolio over the backtest period was: {total_return:.2%}')
    print(f'The backtest period was: {years:.2f} years')   
    print(f'The average annual return of the portfolio over the backtest period was: {(total_return/years):.2%}')
    print(f'The Sharpe Ratio of your portfolio is:{Portfolio_SharpeRatio}')

def player_portfolio_backtest(returns):
    print("Please write in yyyy-mm-dd format!")
    start_date, end_date = collect_dates()
    years = ((pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25)
    returns = returns
    total_return, final_portfolio_value, sharpe = backtest_static(start_date, end_date, returns, initial_capital=1000000)
    return total_return, final_portfolio_value, Portfolio_SharpeRatio, years


def collect_dates():
    start_date =collect_start_date()
    end_date = collect_end_date()
    if pd.to_datetime(start_date) >= pd.to_datetime(end_date):
        start_date, end_date = wrong_order_dates(start_date, end_date)
    return start_date, end_date
def collect_start_date():
    start_date = input("Please enter the start date for the backtest: ")
    if start_date == "m":
        start_date = "2016-01-01"  # Set a default start date
    if pd.to_datetime(start_date, errors='coerce') is pd.NaT:
        print("Invalid date format. Please enter the date in yyyy-mm-dd format.")
        return collect_start_date()
    return start_date

def collect_end_date():
    end_date = input("Please enter the end date for the backtest: ")
    if end_date == "m":
        end_date = "2026-06-08"  # Set a default end date
    if pd.to_datetime(end_date, errors='coerce') is pd.NaT:
        print("Invalid date format. Please enter the date in yyyy-mm-dd format.")
        return collect_end_date()
    return end_date

def wrong_order_dates(start_date, end_date):
    print("End date must be after start date. Which would you like to change?")
    response = input("Type 'start' to change the start date or 'end' to change the end date: ")
    if response == "start":
        start_date = collect_start_date()
    elif response == "end":
        end_date = collect_end_date()
    else:
        print("Invalid response. Please type 'start' or 'end'.")
        return wrong_order_dates(start_date, end_date)
    return start_date, end_date


def backtest_static(start_date, end_date,  returns, initial_capital=0):


    #Reduce the stocks to just the user's portfolio
    portfolio = pd.read_csv('EzQuant/Data/Portfolio/portfolio.csv',index_col=None, header=0)
    portfolio['Value'] = portfolio['Value'].astype(float)
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
    total_portfolio_returns = pd.Series(dtype='float64')
    return_list = []
    current_portfolio_value = initial_capital
    weekly_value_o = 1000000
    for return_index, return_row in returns_change.iterrows():
        weekly_value_i=0
        for portfolio_index, portfolio_row in portfolio.iterrows():
            stock_i_value = portfolio_row['Value']
            stock_i = portfolio_row['Stock']
            stock_i_value = stock_i_value + (stock_i_value * return_row[stock_i])
            weekly_value_i = weekly_value_i + stock_i_value
            portfolio.loc[portfolio_index, 'Value'] = stock_i_value
        weekly_return = (weekly_value_i - weekly_value_o)/weekly_value_o
        weekly_value_o = weekly_value_i
        return_list.append(weekly_return)
        current_portfolio_value = current_portfolio_value*(1+weekly_return)

    """
    Sharpe Ratio = (E(x) - Rf)/SD(x)
    E(x) = expected portfolio return
    Rf = Risk free rate of return: With the volatile nature of stocks, no asset in the portfolio is risk-free
    SD(x) = standard deviation of the portfolio's excess returns

    Consideration to ponder: Because there is a safe return of 0, all portfolios are practically measuring how strong their volatility is (in both upwards and negative direction) 
    """
    final_portfolio_value = current_portfolio_value
    total_portfolio_returns = pd.DataFrame({'Week': returns_change['Date'], 'Weekly_Return': return_list})
    total_portfolio_returns.to_csv(f'EzQuant/Data/Processed/backtest_total_returns.csv', index=False)
    total_return = (final_portfolio_value - initial_capital)/initial_capital




    return total_return, final_portfolio_value, return_list

def backtest_strategy_flexible(data, strategy_func, initial_capital=10000):
    return

def calculate_SD_and_Ex(return_list):
    SD = stat.pstdev(return_list)
    Ex = sum(return_list) / len(return_list)
    return SD, Ex

main()

