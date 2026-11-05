import pandas as pd
import numpy as np
import statistics as stat

def main():
    returns = pd.read_csv('Data/Processed/full_price_history.csv')
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize()
    start_date, end_date = collect_dates()
    shortened_returns = backtest_preperation(returns, start_date, end_date)
    total_return, final_portfolio_value, years = player_portfolio_backtest(shortened_returns, start_date, end_date)
    final_value, values_list = backtest_strategy_value(returns, shortened_returns, start_date, end_date, initial_capital=1000000)
    
    print(f'The final portfolio value is: ${final_portfolio_value:,.2f}')
    print(f'The total return of the portfolio over the backtest period was: {total_return:.2%}')
    print(f'The backtest period was: {years:.2f} years')   
    print(f'The average annual return of the portfolio over the backtest period was: {(total_return/years):.2%}')

def player_portfolio_backtest(total_returns, start_date=None, end_date=None):
    print("Please write in yyyy-mm-dd format!")
    years = ((pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25)
    total_return, final_portfolio_value = backtest_static(start_date, end_date, total_returns, initial_capital=1000000)
    return total_return, final_portfolio_value, years


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


def backtest_preperation(returns, start_date, end_date):
    total_returns = returns.drop(columns=['Date'])
    total_returns = total_returns.pct_change()
    total_returns.insert(0, 'Date', returns['Date'])
    total_returns = total_returns.iloc[1:]  # Remove the first row with NaN values
    total_returns.to_csv(f'Data/Processed/total_backtest_percentage_returns.csv', index=False)

    shortened_returns = total_returns.loc[(total_returns['Date'] >= pd.to_datetime(start_date)) & (total_returns['Date'] <= pd.to_datetime(end_date))]
    shortened_returns.to_csv(f'Data/Processed/shortened_backtest_percentage_returns.csv', index=False)
    return shortened_returns



def backtest_static(start_date, end_date,  shortened_returns, initial_capital=0):


    #Reduce the stocks to just the user's portfolio
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv',index_col=None, header=0)
    portfolio['Value'] = portfolio['Value'].astype(float)
    portfolio_stocks = portfolio['Stock'].tolist()
    portfolio_stocks = ['Date'] + portfolio_stocks
   
    #Calculate the returns of all stocks over the portfolio period
    '''
        in fact this part will need to be changed to be a function that can be called from somewhere else, 
        as the code and data is used in the hedging.py and optimiser.py files as well, which dont actually utilise backtesting
    '''

    portfolio_returns = shortened_returns[portfolio_stocks]

    portfolio_returns_change = portfolio_returns.drop(columns=['Date'])
    portfolio_returns_change.insert(0, 'Date', portfolio_returns['Date'])
    portfolio_returns_change = portfolio_returns_change.iloc[1:]  
    portfolio_returns_change.to_csv(f'Data/Processed/reduced_backtest_percentage_returns.csv', index=False)

    #Calculate average weekly returns of portfolio for each week
    total_portfolio_returns = pd.Series(dtype='float64')
    return_list = []
    current_portfolio_value = initial_capital
    weekly_value_o = portfolio['Value'].sum()  # Initial portfolio value
    for return_index, return_row in portfolio_returns_change.iterrows():
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

    """
    final_portfolio_value = current_portfolio_value
    total_portfolio_returns = pd.DataFrame({'Week': portfolio_returns_change['Date'], 'Weekly_Return': return_list})
    total_portfolio_returns.to_csv(f'Data/Processed/backtest_total_returns.csv', index=False)
    total_return = (final_portfolio_value - initial_capital)/initial_capital




    return total_return, final_portfolio_value

def backtest_strategy_value(data, specified_returns, start_date, end_date, initial_capital=1000000):
    pe_ratios = pd.read_csv('Data/Processed/full_pe_ratios.csv', header=0, index_col=None)
    shortened_pe_ratios = pe_ratios.loc[(pe_ratios['Date'] >= (start_date)) & (pe_ratios['Date'] <= (end_date))]
    print(shortened_pe_ratios)
    purchased_stocks = []
    stock_ratios = []
    value = initial_capital
    values_list = [initial_capital]
    for ratio_index, ratio_row in shortened_pe_ratios.iterrows():
        current_pe_ratio = 100
        for stock_name in specified_returns.columns:
            if stock_name == 'Date':
                continue
            else:
                if ratio_row[stock_name] == 0:
                    continue
                else:
                    
                    if ratio_row[stock_name] <= 25:
                        continue
                    else:
                        if ratio_row[stock_name] < current_pe_ratio:
                            current_pe_ratio = ratio_row[stock_name]
                            stock_to_buy = stock_name
                            stock_ratios.append(current_pe_ratio)
                            purchased_stocks.append(stock_to_buy)
    
        percentage_change = specified_returns.at[ratio_index, stock_to_buy]
        value = value * (1 + percentage_change)
        values_list.append(value)
        print(specified_returns.at[ratio_index, 'Date'])
        if ratio_index >= 50:
                print(f"Week: {ratio_row['Date']}, Stock: {stock_to_buy}, PE Ratio: {current_pe_ratio}, Percentage Change: {percentage_change:.2%}, Portfolio Value: ${value:,.2f}")
    value_returns = pd.DataFrame({'Date': specified_returns['Date'], 'Portfolio_Value': values_list})
    value_returns.to_csv(f'Data/Processed/backtest_value_strategy.csv', index=False)
    return value, values_list

def backtest_strategy_momentum(data, strategy_func, initial_capital=10000):
    return





def calculate_SD_and_Ex(return_list):
    SD = stat.pstdev(return_list)
    Ex = sum(return_list) / len(return_list)
    return SD, Ex

main()

