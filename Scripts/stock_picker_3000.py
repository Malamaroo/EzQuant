import time
import EzQuant.App.Backend.backtest as bt

def main():
    print("yo wsg my g")
    time.sleep(2)
    print("we rdy?")
    time.sleep(1)
    print("ok lets go")
    time.sleep(1)
    print("first you gonna need to choose some stocks, kk?")
    print("write 'done' when you are done choosing stocks")
    all_stock_list = ['AAPL','JNJ','JPM','PG','XOM','NEE','CAT','LIN','PLD','MCD']
    stocks = choose_stocks(all_stock_list)
    weigh_stocks(stocks)



def choose_stocks(all_stock_list):
    stocks = ['JNJ', 'JPM', 'PG', 'XOM',
                'NEE', 'CAT', 'LIN', 'PLD',
                'MCD','WMT','BA','UPS',
                'INTC','V','WM',
                ]
    while True:
        stock = input("Enter a stock ticker (e.g., AAPL, JNJ, JPM): ")
        if stock.lower() == 'done':
            break
        elif stock in all_stock_list:
            print(f"Added {stock} to your portfolio.")
            stocks.append(stock)  
            return stocks     
        else:
            print("Please enter an included stock or type 'done'")
            
    

print("Final stock selection:")


def weigh_stocks(stocks):
    total_weight=0
    stock_list = []
    for stock in stocks:
        stock_dict = {}
        print(f"You Have selected stock: {stock}")
        stock_i_weight = input("please enter the weight of this stock")
        if stock_i_weight != int:
            raise ValueError
        stock_dict["stock"] = stock
        stock_dict["weight"] = stock_i_weight
        total_weight = total_weight + stock_i_weight
        stock_list = stock_list + stock_dict
    print(stock_list)



main()

