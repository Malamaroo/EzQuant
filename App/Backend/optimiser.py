
"""
Library usage: pandas used for data collection and manipulation, numpy used for the square root
function, and pypfopt used to maximise returns for a given level of risk.
"""

import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier

#Note: for the following script, I would have preferred to have made low risk lower, but I have come to understand that the function efficient_risk(risk) will only work when the risk is high enough, and via my own testing, I discovered this to be the minimum. Of course, this depends on the size of the portfolios involved (as in how many stocks), but wanting to ensure users can choose as much as possible, the lowest default is only as low as is viable for a small portfolio.
#^^This sentence is a bit wordy, sorry for that.

def user_risk_comfortability(): #collect the user's desired level of yearly risk (volatility). This function is only called when the file is run directly, not when it is called from the frontend; as the risk is collected by the frontend.
    choice = input("Would you like to choose from risk comfortability presets (1) or input your own desired risk (2)? ")
    if choice == '1': #if the user would like to choose from the presets
        print("Please choose from the following risk comfortability presets:")
        print("1. Low Risk (15%)")
        print("2. Medium Risk (25%)")
        print("3. High Risk (40%)")
        preset_choice = input("Enter the number corresponding to your choice: ")
        if preset_choice == '1': #each preset corresponds to a yearly volatility, returned as a decimal
            return 0.15
        elif preset_choice == '2':
            return 0.25
        elif preset_choice == '3':
            return 0.4
        else: #error management, if the user inputs an invalid response, default to medium risk
            print("Invalid choice. Defaulting to Medium Risk (25%).")
            return 0.25
    elif choice == '2': #if the user would like to input their own level of risk
        user_input = input("Please enter your desired risk tolerance (as a decimal, e.g., 0.01 for 1%): ")
        try:
            user_desired_risk = float(user_input) #convert the user's input to a float, so it can be used by the optimiser
            return user_desired_risk
        except ValueError: #error management, if the input cannot be converted to a number, default to medium risk
            print("Invalid input. Defaulting to Medium Risk (25%).")
            return 0.25

def mean_variance_optimisation(means_returns, cov_matrix, risk, min_weight): #find the weights that give the highest expected return for the user's level of risk, using mean-variance optimisation (pypfopt's efficient frontier).

    ef = EfficientFrontier(means_returns, cov_matrix, weight_bounds=(min_weight, 0.95)) #build the efficient frontier; every stock must have at least min_weight and no single stock can be more than 95% of the portfolio
    try:
        weights = ef.efficient_risk(risk) #maximise return for a target volatility; this fails if the target risk is not achievable with the given stocks, hence the try/except
        return weights #a dictionary of each stock and its optimal weight
    except Exception as e: #error management, if no solution exists for the specified risk, report the issue and return nothing so run_optimisation() can handle it
        print(f"An error occurred during mean-variance optimization: {e}")
        return None

def prepare_optimisation(): #gather the data the optimiser requires: the average return of each stock, the covariance between each stock, and the minimum weight.
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv', index_col=None, header=0) #read in the user's current portfolio
    stocks = portfolio['Stock'].tolist() #create a list of the stock (names) in the user's portfolio, only these stocks are optimised

    returns = pd.read_csv('Data/Processed/total_backtest_percentage_returns.csv') #read in the weekly percentage changes of all stocks (created in backtest.py)
    returns = returns.drop(columns=['Date'])[stocks] #remove the date column and reduce the returns to just the user's portfolio stocks

    mean_returns = returns.mean() #the average weekly return of each stock
    cov_matrix = returns.cov() #the covariance of every stock with every other stock, used to measure the portfolio's risk

    min_weight = 0.001 #the minimum weight of each stock (0.1%), ensures that every stock the user selected remains in the portfolio to at least some degree
    return mean_returns, cov_matrix, min_weight


def run_optimisation(yearly_risk): #optimises the user's portfolio for their desired yearly risk, and saves the new portfolio. This function is called by main() and directly by the frontend.
    weekly_risk = yearly_risk / np.sqrt(52) #convert the yearly risk to weekly risk, as the returns are weekly; volatility scales with the square root of time (52 weeks in a year)
    mean_returns, cov_matrix, min_weight = prepare_optimisation() #gather the data required for the optimisation
    weights = mean_variance_optimisation(mean_returns, cov_matrix, weekly_risk, min_weight) #find the optimal weights for the user's stocks
    if weights is None: #error management, if the optimisation failed, tell the user and return nothing
        print("Optimization failed. No weights returned.")
        return None

    portfolio = pd.DataFrame.from_dict(weights,orient='index', columns=['Weight']) #convert the dictionary of weights to a dataframe
    portfolio = portfolio.reset_index().rename(columns={'index': 'Stock', 0: 'Weight'}) #move the stock names from the index into their own column, to match the structure of portfolio.csv
    value_list = [] #an empty list designed to house the value of each stock in the portfolio
    for portfolio_index, portfolio_row in portfolio.iterrows(): #for each stock in the portfolio, calculate how much money is put into it.
        stock_value_i = portfolio_row['Weight']*1000000 #the value of the stock is its weight multiplied by the initial capital ($1,000,000, as used in the backtest)
    #it was an intentional design decision to multiply by 1,000,000 rather than the initial_capital, as the optimisation is meant to optimise the user's ENTIRE portfolio (which would also include their cash)
        value_list.append(stock_value_i)
    portfolio['Value'] = value_list #add the values to the portfolio, so it has the same columns as before the optimisation
    portfolio.to_csv('Data/Portfolio/portfolio.csv', index=False) #overwrite the user's portfolio with the optimised one, so it is used by the backtest and hedging
    return portfolio

def main(): #the main() function that only runs when this file is directly run, collects the user's risk via the console, optimises the portfolio, and prints it.
    risk = user_risk_comfortability()
    portfolio = run_optimisation(risk)
    print(portfolio)

if __name__ == "__main__": #only run main() if this file is directly called
    main()
