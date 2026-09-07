import pandas as pd
from fredapi import Fred
import statistics as stat

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


def main():
    return_list = pd.read_csv('Data/Portfolio/portfolio_returns.csv')
    return_list = return_list['Portfolio_Return'].tolist()
    SD, Ex = calculate_SD_and_Ex(return_list)
    RFR =set_risk_free_rate()
    SR = calculate_sharpe_ratio(SD, Ex, RFR)
    print(f"The Sharpe Ratio of your portfolio is {SR} with a risk free rate of {RFR}")

main()