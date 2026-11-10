"""
Library usage: pandas used for data collection and manipulation.
"""
#There is one issue with this code, but at this point - as is correborated by the step-by-step style of the frontend - I have left to ensure that users follow through with each step; of course, this is the issue that the optimiser.py file requires this file to have previously been run in order to utilise its covariance matrix. This creates a sort of dependency, but a just established, has been framed to not be an error.

import pandas as pd


def hedge(): #Hedge function. This function evaluates the user's current portfolio, and suggests another stock to be purchased in order to minimise the portfolio's variance, thus hedging risk. This function is called by main() and directly by the frontend.
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv',index_col=None, header=0) #read in list of stocks and their weights in portfolio (all data is saved as CSVs to be easily accessed, readable, and straightforward to call later.)
    returns = pd.read_csv('Data/Processed/total_backtest_percentage_returns.csv') #read in list of percentage changes for every day.
    portfolio_returns = reduce_to_portfolio(returns, portfolio) #reduce all stocks to just the stocks the user has decided for their portfolio.
    build_portfolio_cov_matrix(portfolio_returns, portfolio) #build cov matrix comprised of solely portfolio stocks. 
    total_portfolio_returns = calculate_total_portfolio_returns(portfolio_returns, portfolio) #calculate the theoretical total returns of the user's portfolio, based on the percentage change of each stock in the portfolio and the weight of said stock in the portfolio.
    covariance_matrix = build_adapted_covariance_matrix(total_portfolio_returns, portfolio) #create a covariance matrix comprised of the portfolio (a single value that houses all of the portfolio's stocks) and all non-portfolio stocks
    stock_recommendation, covariance_value = recommend_hedge(covariance_matrix) #recommend the best stock to hedge the user's portfolio based on the covariance matrix of all stocks and the user's portfolio.
    return stock_recommendation, covariance_value

def reduce_to_portfolio(returns, portfolio): #reduce a selection of all stocks to just the stocks the user has decided for their portfolio.
    portfolio['Value'] = portfolio['Value'].astype(float) #ensure that the value column (of how much each stock is worth in the portfolio) is a float.
    portfolio_stocks = portfolio['Stock'].tolist() #create a list of the names of each stock
    portfolio_stocks = ['Date'] + portfolio_stocks #add 'date' with the list of stocks, so returns can be reduced to required stocks + portfolio stocks.
    portfolio_returns = returns[portfolio_stocks] #reduce the returns df of all stocks to just the stocks in the portfolio + date
    return portfolio_returns


def build_portfolio_cov_matrix(returns, portfolio):  #function designed to create a covariance matrix of all stocks included in the user's portfolio. This is then used for optimisation.
    returns_change = returns.drop(columns=['Date']) #remove the date data, so covariance (on lists of floats rather than datettime) can be calculated for each stock in the portfolio.
    returns_change.cov().to_csv(f'Data/Portfolio/covariance_matrix.csv', index=True) #calculate the cov matrix of just included portfolio and then save it as a CSV for later use.
    returns_change.insert(0, 'Date', returns['Date']) #re-insert the date column, so returns can be calculated for each week in the portfolio.
    

def calculate_total_portfolio_returns(returns_change, portfolio): #function designed to calculate the total returns of the user's portfolio, based on the percentage change of each stock in the portfolio and the weighting of each stock in the portfolio.
    return_list = [] #an empty list designed to house the portfolio's return for each week of avaliable stock history.
    for return_index, return_row in returns_change.iterrows(): #for each week: (This code is much like and is in fact based upon what was created for backtest.py)
        weekly_value_i = 0  
        for portfolio_index, portfolio_row in portfolio.iterrows(): #for each stock in the portfolio, times its weight by its return.
            stock_i_value = portfolio_row['Weight'] #get stock's value
            stock_i = portfolio_row['Stock'] #get stock's name
            stock_i_value = stock_i_value * return_row[stock_i] #set the new value, to the current value multiplied by the return (this is to calculate the return for that week)
            portfolio.loc[portfolio_index, 'Value'] = stock_i_value #update the value to the new return /// 
            weekly_value_i = weekly_value_i + stock_i_value #add the return to the weekly return
        return_list.append(weekly_value_i) #append the return to the list of returns
    total_portfolio_returns = pd.DataFrame({'Date': returns_change['Date'], 'Portfolio_Return': return_list}) #create a dataframe of the weekly returns with their corresponding date
    total_portfolio_returns.to_csv(f'Data/Portfolio/portfolio_returns.csv', index=False)
    print(total_portfolio_returns)
    return total_portfolio_returns #will be used in the creation of the covariance matrices.



def build_adapted_covariance_matrix(portfolio_returns, portfolio): #create the "adapted" covariance matrix, a covariance matrix that compares the covariance of the portfolio and all other non-portfolio stocks.
    remove_stocks = portfolio['Stock'].tolist() #create a list of all stock names in the portfolio to be used to remove them from all stocks.

    all_returns = pd.read_csv('Data/Processed/full_price_history.csv', header=0, index_col=None) #read full price history of all stocks
    all_returns_refined = all_returns.drop(columns=['Date']) #temporarily remove date, to convert returns to percentage changes
    all_returns_refined = all_returns_refined.pct_change() #calculate the percentage change of each week
    all_returns_refined.insert(0, 'Date', all_returns['Date']) #re-input the date column
    all_returns_refined = all_returns_refined.iloc[1:].reset_index(drop=True) #remove the first row which now has NaN, and then reset_index (so the 1st row is index 0). This may or may not have fixed the following problem regarding the CPU load limits and pd.concat() not working, but I was too unsure to check, and thus have kept it as it is - working.
    all_returns_refined['Date'] = pd.to_datetime(all_returns_refined['Date'], utc=True).dt.date  ###ensuring that date formats are the same for both dataframes

    #the following script is designed to merge the returns of all non-portfolio stocks with that of the portfolio, originally this used pd.concat() which merges dataframes on a mutual column, this stopped working because of something to do with the index not being the same; it may now work, but as just stated, I didnt want to alter something already working.
    portfolio_returns = portfolio_returns.drop(columns=['Date']) ### The following script was designed because of restrictive CPU load times which limits how data can be transferrred and therefore it leads to nothing being visible.
    merged_returns = pd.concat([all_returns_refined, portfolio_returns], axis=1) #effectively put the two dataframes next to each other
    merged_returns = merged_returns.drop(columns=['Date']) #drop the date column in order to turn the new merged dataframe into a covariance matrix
    merged_returns = merged_returns.rename(columns={'Portfolio_Return': 'Portfolio'}) #rename portfolio_return to just "portfolio" to be more aesthetic and match the data naming structure used for the other returns which is just the asset's name (ticker)
    merged_returns = merged_returns.drop(columns=remove_stocks) #remove all portfolio stocks
    covariance_matrix = merged_returns.cov() #calculate the covariace of all remaining (including the portfolio itself)
    covariance_matrix.to_csv('Data/Portfolio/adapted_covariance_matrix.csv') #save this to a csv (will be called by optimiser.py)
    return covariance_matrix


def recommend_hedge(covariance_matrix): #recommend the player the hedge asset
    covariance_matrix = covariance_matrix.drop(index='Portfolio') #remove the portfolio row, so that only the portfolio column remains (recall that a covariance matrix is a table in which the rows are equivalent to the columns)
    cov_value_i = 1.1 #set the default (lowest) covariance to 1.1 a number literally unachieavable.
    for cov_index, cov_row in covariance_matrix.iterrows(): #iterate over each row of the covariance matrix, to find the most negative covariance with the portfolio.
        cov_value_o = cov_row['Portfolio'] #cov_value_o = the current stock's covariance with the portfolio
        if cov_value_o < cov_value_i: #if a new lowest covariance is found, recommend the stock and return the corresponding covarance
            stock_recommendation = cov_index
            cov_value_i = cov_value_o
    return stock_recommendation, cov_value_i #return the stock recommended for hedging and its covariance

   
   
   
def main(): #the main() function that only runs when this file is directly run, ultimately runs the entire hedging process in the exact same way that the frontend does.
    stock_recommendation, covariance_value = hedge()
    print(f"The best stock to hedge your portfolio is {stock_recommendation} with a covariance value of {covariance_value}")
   
  
if __name__ == '__main__': #only run main() if this file is directly called
    main()