import pandas as pd
from fredapi import Fred
import statistics as stat
import numpy as np
from pypfopt import EfficientFrontier, expected_returns, risk_models

def calculate_stats(return_list):
   SD, Ex = calculate_SD_and_Ex(return_list)
   RFR = set_risk_free_rate()
   SR = calculate_sharpe_ratio(SD, Ex, RFR)
   return SD, Ex, RFR, SR

def calculate_SD_and_Ex(return_list):
    SD = stat.pstdev(return_list)/100
    Ex = sum(return_list) / len(return_list)/100
    print(SD, Ex)
    return SD, Ex


def calculate_sharpe_ratio(SD, Ex, RFR):
    if SD != 0:
        SharpeRatio = (Ex - RFR) / (SD) 
    else:
        SharpeRatio = 0
    return SharpeRatio


def set_risk_free_rate():
    fred = Fred(api_key='8046fbc851bd73423658b8dd1572432b')
    ten_year_treasury_rate = fred.get_series_latest_release('DGS10')/100
    risk_free_rate = ten_year_treasury_rate.iloc[-1]

    return risk_free_rate


def user_risk_comfortability():
    choice = input("Would you like to choose from risk comfortability presets (1) or input your own risk free rate (2)? ")
    if choice == '1':
        print("Please choose from the following risk comfortability presets:")
        print("1. Low Risk (5%)")
        print("2. Medium Risk (15%)")
        print("3. High Risk (30%)")
        preset_choice = input("Enter the number corresponding to your choice: ")
        if preset_choice == '1':
            return 0.05
        elif preset_choice == '2':
            return 0.15
        elif preset_choice == '3':
            return 0.30
        else:
            print("Invalid choice. Defaulting to Medium Risk (15%).")
            return 0.15
    elif choice == '2':
        user_input = input("Please enter your desired risk tolerance (as a decimal, e.g., 0.01 for 1%): ")
        try:
            user_risk_comfortability = float(user_input)
            return user_risk_comfortability
        except ValueError:
            print("Invalid input. Defaulting to Medium Risk (15%).")
            return 0.15

def maximise_return_for_risk():
    raise

def mean_each_stock_return(portfolio):
    returns = pd.read_csv('Data/Processed/total_backtest_percentage_returns.csv')
    reduced_stocks = portfolio['Stock'].tolist()
    returns = returns.drop(columns=['Date'])
    returns = returns[reduced_stocks]
    mean_returns = returns.mean()
    
    

    return mean_returns


def mean_variance_optimisation(means_returns, cov_matrix, risk, min_weight):

    ef = EfficientFrontier(means_returns, cov_matrix, weight_bounds=(min_weight, 0.95))
    try:
        weights = ef.efficient_risk(risk)
        cleaned_weights = ef.clean_weights()
        return weights
    except Exception as e:  
        print(f"An error occurred during mean-variance optimization: {e}")
        return None

def prepare_optimisation():
    risk = user_risk_comfortability()
    portfolio = pd.read_csv('Data/Portfolio/portfolio.csv', index_col=None, header=0)
    mean_returns = mean_each_stock_return(portfolio)
    cov_matrix = pd.read_csv('Data/Portfolio/covariance_matrix.csv', index_col=0)
    n_stocks = len(portfolio)
    min_weight = (85 / n_stocks) / 100
    return risk, mean_returns, cov_matrix, min_weight
def main():
    return_list = pd.read_csv('Data/Portfolio/portfolio_returns.csv')
    return_list = return_list['Portfolio_Return'].tolist()
 
    """ plug this in somewhere to get statistics of investment strategy and thus understand the productivity of it.
        SD, Ex, RFR, SR = calculate_stats(return_list)
    """
    risk, mean_returns, cov_matrix, min_weight = prepare_optimisation()
    print(risk)
    weights =mean_variance_optimisation(mean_returns, cov_matrix, risk, min_weight)
    print(weights)
    portfolio = pd.DataFrame.from_dict(weights,orient='index', columns=['Weight'])
    portfolio = portfolio.reset_index().rename(columns={'index': 'Stock', 0: 'Weight'})
    value_list = []
    for portfolio_index, portfolio_row in portfolio.iterrows():
        stock_value_i = portfolio_row['Weight']*1000000
        value_list.append(stock_value_i)
    portfolio['Value'] = value_list
    portfolio.to_csv('Data/Portfolio/portfolio.csv', index=False)


main()