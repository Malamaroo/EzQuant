

"""
Library usage: pandas used for data collection and manipulation.
"""
import pandas as pd

def main(): #The main function that collects the start and end dates for the backtest, runs it, and compares against the P/E strategy. This only runs when the file is run directly.
    returns = pd.read_csv('Data/Processed/full_price_history.csv') # Read the price history data collected in the data collection stage
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize() #convert the dates of the price history data to be compatible with the pandas functions.
    start_date, end_date = collect_dates() #collect user's desired start and end dates for the backtest
    shortened_returns = backtest_preperation(returns, start_date, end_date) #prepare the returns data for the backtest (reduce to just between the desired dates)
    total_return, final_portfolio_value, years, values_list, dates_list = player_portfolio_backtest(shortened_returns, start_date, end_date) #run the backtest on the user's portfolio between the desired dates
    final_value, pe_values_list, pe_dates_list  = backtest_strategy_value(returns, shortened_returns, start_date, end_date, initial_capital=1000000) #run the backtest on the P/E trading strategy between the same dates


    #print the results of the backtest in the console
    print(f'The final portfolio value is: ${final_portfolio_value:,.2f}')
    print(f'The total return of the portfolio over the backtest period was: {total_return:.2%}')
    print(f'The backtest period was: {years:.2f} years')   
    print(f'The average annual return of the portfolio over the backtest period was: {(total_return/years):.2%}')

def player_portfolio_backtest(total_returns, start_date=None, end_date=None): #runs the backtest on the user's portfolio. This function is to be called either in main() or from the frontend via run_backtest(), thus it is a seperate function from main().
    years = ((pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25) #Calculate the total amount of years of the backtest (as a float) to return to the user
    total_return, final_portfolio_value, values_list, dates_list = backtest_static(start_date, end_date, total_returns, initial_capital=1000000) #function that conducts the backtest on the user's portfolio between specified dates
    return total_return, final_portfolio_value, years, values_list, dates_list #return the results of the backtest to the user

def run_backtest(start_date, end_date): #the function that is called from the frontend to run a backtest on the user's portfolio and the P/E strategy between specified dates. This function takes the parameters start_date and end_date from the frontend, which is inputted via a visual date selector.
    returns = pd.read_csv('Data/Processed/full_price_history.csv') #collect the price history data to be used in the backtest
    returns['Date'] = pd.to_datetime(returns['Date'], utc=True).dt.tz_localize(None).dt.normalize() #convert the dates of the price history data to be compatible with the pandas functions.
    shortened_returns = backtest_preperation(returns, start_date, end_date) #prepare the returns data for the backtest (reduce to just between the desired dates)
    total_return, final_portfolio_value, years, values_list, dates_list = player_portfolio_backtest(shortened_returns, start_date, end_date) #run the backtest on the user's portfolio between the desired dates
    pe_final_value, pe_values_list, pe_dates_list  = backtest_strategy_value(returns, shortened_returns, start_date, end_date, initial_capital=1000000) #run the backtest on the P/E trading strategy between the same dates
    
    backtest_data = { #create a dictionary with all the relevant data to be returned to the frontend to display it to the user
        'dates': [date.strftime('%Y-%m-%d') for date in dates_list],
        'values': values_list,
        'final_portfolio_value': final_portfolio_value,
        'total_return': total_return,
        'years': years,
        'average_annual_return': (total_return / years),
        'pe_values': pe_values_list,
        'pe_final_value': pe_final_value,
        'pe_total_return': (pe_final_value - 1000000) / 1000000,
    }
    return backtest_data #return the dictionary to the frontend to be displayed to the user


"""
For the following code, there is a considerable error; when data is pulled it does not
go back until the beginning of history or into the future, so entering a time outside
of its range will not lead to accurate results in the backtest. However, this problem
is only in the backend, as the frontend has hardcapped minimum and maximum dates.
"""


def collect_dates(): #collect the start and end dates for the backtest from the user. This function is only called when the file is run directly, not when it is called from the frontend; as the process is hard coded into the frontend.
    start_date =collect_start_date() #collect the start date for the backtest,it is a seperate function to make error management simple 
    end_date = collect_end_date() #collect the end date for the backtest, it is a seperate function to make error management simple 

#error management, if start date is after the end date, reprompt the user for dates
    if pd.to_datetime(start_date) >= pd.to_datetime(end_date): 
        start_date, end_date = wrong_order_dates(start_date, end_date) 
    return start_date, end_date
def collect_start_date(): #collect the start date
    start_date = input("Please enter the start date for the backtest: ")
    if start_date == "m": #"m" for master, a default date is set for testing purposes
        start_date = "2016-01-01"  # set the default date
    if pd.to_datetime(start_date, errors='coerce') is pd.NaT: #error management, if it doesnt fit the right date structure, reprompt user to enter date
        print("Invalid date format. Please enter the date in yyyy-mm-dd format.")
        return collect_start_date() #restart selecting start date process
    return start_date

def collect_end_date():
    end_date = input("Please enter the end date for the backtest: ")
    if end_date == "m": #"m" for master, a default date is set for testing purposes
        end_date = "2026-06-08"  # Set a default end date
    if pd.to_datetime(end_date, errors='coerce') is pd.NaT: #error management, if it doesnt fit the right date structure, reprompt user to enter date
        print("Invalid date format. Please enter the date in yyyy-mm-dd format.")
        return collect_end_date() #restart selecting end date process
    return end_date

def wrong_order_dates(start_date, end_date): #error management, if the dates are the wrong order, ask them to change either date.
    print("End date must be after start date. Which would you like to change?")
    response = input("Type 'start' to change the start date or 'end' to change the end date: ")
    if response == "start": #if the user would like to change start, reperompt them for a new start date
        start_date = collect_start_date()
    elif response == "end": #if the user would like to change end, reperompt them for a new end date
        end_date = collect_end_date()
    else: #if the user inputs an invalid response, reprompt them for a valid response
        print("Invalid response. Please type 'start' or 'end'.")
        return wrong_order_dates(start_date, end_date)
    return start_date, end_date

def backtest_preperation(returns, start_date, end_date): #prepare the returns data for the backtest; change data to be percent changes and reduce the returns data to be just between the desired start date and end date.
    total_returns = returns.drop(columns=['Date']) #momentarily remove the data column to calculate the percent changes of all stocks in the returns data
    total_returns = total_returns.pct_change() #calculate the percentage change of each row
    total_returns.insert(0, 'Date', returns['Date']) #reinsert the date column back into the returns date
    total_returns = total_returns.iloc[1:]  # Remove the first row with NaN values + the redundant first date
    total_returns.to_csv(f'Data/Processed/total_backtest_percentage_returns.csv', index=False) #save this data to a csv file for dev and user analysis

    shortened_returns = total_returns.loc[(total_returns['Date'] >= pd.to_datetime(start_date)) & (total_returns['Date'] <= pd.to_datetime(end_date))] #reduce the percentage returns to be only between the user's specified dates, this is done via pandas.
    shortened_returns.to_csv(f'Data/Processed/shortened_backtest_percentage_returns.csv', index=False) #save this data to a csv file for use in the backtest and for dev and user analysis
    return shortened_returns



def backtest_static(shortened_returns, initial_capital=0): #the function that runs the backtest on the user's portfolio between the user's desired dates.
    
    """
    Step 1: Reduce the shortened percentage change data to just the user's portfolio
    """
    #Reduce the stocks to just the user's portfolio
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv',index_col=None, header=0) #read in the user's portfolio
    portfolio['Value'] = portfolio['Value'].astype(float) #ensure all values are read as floats (it would be unusual for them not to be, but just a precaution); this is relevant for the calculations of returns.
    portfolio_stocks = portfolio['Stock'].tolist() #Create a list of the stock (names) in the user's portfolio
    portfolio_stocks = ['Date'] + portfolio_stocks #create a list of the stock (names) in the user's portfolio, with 'Date' as the first element to ensure the date column is included in the reduced data
    portfolio_returns = shortened_returns[portfolio_stocks] #reduce the percentage change data to just the user's portfolio stocks and the date column
    portfolio_returns_change = portfolio_returns.iloc[1:]   # drop the first row (the base date, to ensure that the portfolio experiences just percentage changes that have not occured at the time of beginning, rather than an additional value that has already happened before the backtest period begins)
    portfolio_returns_change.to_csv(f'Data/Processed/reduced_backtest_percentage_returns.csv', index=False) #save the portfolio percentage returns to a csv file for dev and user analysis

    """
    Step 2: Calculate the weekly returns of the portfolio over the backtest period
    """
    total_portfolio_returns = pd.Series(dtype='float64') #create an empty pandas series to store the weekly returns of the portfolio over the backtest period
    return_list = [] #create an empty list to store the weekly returns of the portfolio over the backtest period (this is used to calculate the SD and Ex of the portfolio's returns over time)
    current_portfolio_value = initial_capital #creates a variable to store the value of the portfolio for each iteration
    weekly_value_o = portfolio['Value'].sum()  # Initial portfolio value (will be =< $1,000,000 = initial_capital)
    cash = initial_capital - weekly_value_o #calculate the cash that the user has not invested in the portfolio (this is relevant as it wont experience the same capital gains/losses as the stocks). Important note: This program does not account for monetary inflation.
    values_list = [initial_capital] #create a list to store the value of the (investment) portfolio over time (this is used to plot the portfolio value over time in the frontend); of course the initial value is equivalent to the user's intiial capital
    dates_list = [shortened_returns['Date'].iloc[0]] #create a list to store the dates of the portfolio value over time (this is used to plot the portfolio value over time in the frontend); the initial value is the user's specified start date for the backtest. Each date will correspond to the value of the portfolio at that date in values_list.
    for return_index, return_row in portfolio_returns_change.iterrows(): #calculate the weighted returns of each week; iterates over every week included in the backtest period, and calculates the value of the portfolio at the end of that week.
        #the weekly_return is calculated by recording the percentage change of the portfolio's value from one week to the next
        weekly_value_i=0 #as weekly_value_i is the value of the portfolio at the end of the week, it is reset to 0 at the beginning of each iteration, and then calculated by adding the value of each stock in the portfolio at the end of that week.
        """
        Step 2.5: Calculate the value of the portfolio at the end of the week, by iterating over each stock in the portfolio's increase/decrease
        """
        for portfolio_index, portfolio_row in portfolio.iterrows(): #iterate over each stock in the user's portfolio, calculating the value of that stock at the end of the week, and adding it to the total of weekly value.
            stock_i_value = portfolio_row['Value'] #get the value of the current stock (stock_i) at the beginning of the week
            stock_i = portfolio_row['Stock'] #get the name of the current stock (stock_i) to use as a key to get the percentage change of that stock for that week from the portfolio_returns_change dataframe
            stock_i_value = stock_i_value + (stock_i_value * return_row[stock_i]) # to calculate the final value of stock_i for the week; multiply the value of the stock at the beginning of the week by the percentage change of that stock for that week, and then add it to the stock's value at the beginning of the week.
            weekly_value_i = weekly_value_i + stock_i_value #add the value of stock_i to the toal of weekly_value_i
            portfolio.loc[portfolio_index, 'Value'] = stock_i_value #update the value of stock_i in the portfolio, so it can be accessed for the next week.
        weekly_return = (weekly_value_i - weekly_value_o)/weekly_value_o #calculate the weekly percentage return
        weekly_value_o = weekly_value_i #update the value of the portfolio at the beginning of the next week to be the value of the portfolio at the end of this week
        return_list.append(weekly_return)#add the weekly return to the list of weekly returns, to be used to calculate the SD and Ex of the portfolio's returns over time
        current_portfolio_value = weekly_value_i + cash #calculate the current value of the portfolio, including the cash that is not invested
        values_list.append(current_portfolio_value) #add the current week's portfolio value to a list, to be used to plot the portfolio value over time
        dates_list.append(return_row['Date'])#add the current week's end date to a list, to be used to plot the portfolio value over time [lines up with values_list]

    """
    Step 3: Calculate the final portfolio value and total return of the portfolio over the backtest period
    """


    final_portfolio_value = current_portfolio_value #the final value of the portfolio is equal to the final current_portfolio_value. This variable is redundant other than being more digestible and aesthetic for developers.
    total_portfolio_returns = pd.DataFrame({'Week': portfolio_returns_change['Date'], 'Weekly_Return': return_list}) #create a dataframe to store the weekly returns of the portfolio over the backtest period, to be used to calculate the SD and Ex of the portfolio's returns over time
    total_portfolio_returns.to_csv(f'Data/Processed/backtest_total_returns.csv', index=False) #save the weekly returns of the backtest for dev and user analysis
    total_return = (final_portfolio_value - initial_capital)/initial_capital #calculate the total return of the portfolio over the entire backtest period




    return total_return, final_portfolio_value, values_list, dates_list 

def backtest_strategy_value(data, specified_returns, start_date, end_date, initial_capital=1000000): #function that performs the backtest on the P/E trading strategy between the user's specified dates. This function is called from main() or run_backtest() to compare the user's portfolio against the P/E strategy.
    """
    What is the "P/E Strategy?" It is a design founded upon the idea that a stock's price is not always reflective of its true value. 
    The P/E ratio is a measure of how much investors are willing to pay for a stock's earnings. A high P/E ratio indicates that investors
    are willing to pay more for a stock, often signifying the stock is overvalued; conversly, a low P/E ratio indicates that investors are 
    willing/inclined to spend comparatively less for a stock, often signifying the stock is undervalued. Therefore, the P/E strategy works by:
    1. calculating the P/E ratio of all stocks in the market (in this case, all the stocks avaliable to the user) for each week
    2. Selecting the stock with the lowest P/E ratio (the most undervalued stock) and purchasing it for the week
    3. Therefore, this purchase will experience the following week's percentage change
    4. This will repeat, putting %100 of the strategy's capital allowance into the stock with the lowest P/E ratio for each week\
    
    Therefore, the strategy operates by always looking for and investing in the most undervalued stock. Conceptually it is fine, but I've realised
    it is actually a suboptimal trading strategy, because it may not necessarily give the undervalued companies the time they require to grow or 
    for their values to be regulated - thus not fully maximising the notion of value investing. A better trade would - theoretically - be holding onto an undervalued company
    and perhaps even buy more, until it is no longer undervalued. 
    """
    pe_ratios = pd.read_csv('Data/Processed/full_pe_ratios.csv', header=0, index_col=None) #read in the P/E ratios of all stocks in the market (in this case, all the stocks avaliable to the user) for each week
    shortened_pe_ratios = pe_ratios.loc[(pe_ratios['Date'] >= (start_date)) & (pe_ratios['Date'] <= (end_date))] #reduce the P/E ratios to be only between the user's specified dates, this is done via pandas.
    purchased_stocks = [] #create a list of the stock purchased for each week
    stock_ratios = [] #create a list of the P/E ratios of the selected stock for each week
    value = initial_capital #ensure the program starts with the same capital as the user's portfolio
    values_list = [initial_capital] #add initial value as the first value in the list of values over time (used to visually display the returns over time in the front end)
    dates_list = [specified_returns['Date'].iloc[0]] #add the first date as the first value in the list of dates over time (used to visually display the returns over time in the front end)

    #For each week in the shortened PE list, find the lowest P/E, put money into the corresponding stock, and apply the following week's percentage change.
    for ratio_index, ratio_row in shortened_pe_ratios.iterrows(): #iterate through each week of the P/E ratios
        current_pe_ratio = 100 #set the P/E ratio of comparison to 100 (higher than anything we will go with)
        stock_to_buy = None #set the default stock_to_buy to nothing
        next_index = ratio_index + 1 #establish the next index, to prepare to apply the next week's percentage change
        if next_index not in specified_returns.index: #if next_week is not included in the user's specified dates (as in it is the last week), break
            break
        for stock_name in specified_returns.columns: #iterate through each stock in week_I's P/E ratios
            if stock_name == 'Date': # of course, skip date
                continue
            else:
                if ratio_row[stock_name] <= 0: # if the P/E ratio of the stock is less than or equal to 0 skip, this implies the company either earns nothing or is actively losing money.
                    continue
                else:
                    
                    if ratio_row[stock_name] <= 25: #if the P/E is lower than 25, continue. The only reason this is seperated from the branch above is to differentiate the purpose of each check. Common trader practice is to regard a P/E ratio of less than 25 as suboptimal because such a low ratio could mean that a company is declining - particularly in the extravagant growth that is characteristic of the 21st century.
                        continue
                    else:
                        if ratio_row[stock_name] < current_pe_ratio: #if there is a ratio lower than the currently iterated stock, make that the stock_to_buy
                            current_pe_ratio = ratio_row[stock_name] #update the current pe ratio, as it is now the lowest.
                            stock_to_buy = stock_name #update to be the corresponding stock name
                            
                            
        if stock_to_buy is not None:
            stock_ratios.append(current_pe_ratio) #add the lowest ratio of week_i to the ratios list
            purchased_stocks.append(stock_to_buy) #add the chosen stock of week_i to the stocks list
            percentage_change = specified_returns.at[next_index, stock_to_buy] #retrieve the percentage change to apply to the stocks value. This is found at the chosen's stocks percentage change for the following week.
            value = value * (1 + percentage_change) #update the value, incorporating the percentage change.
        values_list.append(value) #add the current week's value to the values_list (used to present the growth over time as a chart)
        dates_list.append(specified_returns.at[next_index, 'Date']) #add the current week's date [to be more accurate, this is the week that the trade actually experiences] to the values_list (used to present the growth over time as a chart)
        print(specified_returns.at[next_index, 'Date']) 

    return value, values_list, dates_list 

"""
Momentum-based strategy. This strategy is founded upon the belief that upwards momentum can (and does) continue.
Therefore this strategy buys into a stock based on how it has performed in the past 6 month; purchasing THE stock
with the highest momentum (the highest growth at that 6 months ago mark).
"""
#unfortunately, this has not be developed.

def backtest_strategy_momentum(data, strategy_func, initial_capital=10000):
    return




if __name__ == "__main__": #run the function main() if this file is directly ran rather than called.
    main()

