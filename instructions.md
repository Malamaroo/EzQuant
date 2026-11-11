# EzQuant

EzQuant is a website that teaches you the basics of portfolio management (based on Markowitz's Modern Portfolio Theory). You get $1,000,000, pick your stocks, hedge them, optimise them for your risk, and then backtest them against a value investing strategy.

## A note i'd like to make

You have probably noticed that this architecture is quite different to what I originally planned. I quickly realised a lot of the file structure was actually quite inferior, and during development I ultimately saw the project morph to these files and this folder structure. Furthermore, the biggest architecture change is no doubt seen in the front end, but I discovered that this is required for the flask API structure that I used for frontend. So, that is that.

## How to run it

1. Install Python (I used 3.13), then install the packages:

```
pip install pandas numpy yfinance flask pyportfolioopt
```

2. Only if you need to, pull the stock data. Run everything from the main EzQuant folder, otherwise the file paths break. 

```
python Scripts/request_stock_data.py
```

You probably don't need to do this, as the data is already in the Data folder. It downloads 20 years of data for every stock, which takes ages and Yahoo Finance can rate limit you. Only run it if the data is missing or you want newer data (and if you do, run one backtest before hedging/optimising, as they use a file the backtest makes, highlight the unfortunate file dependency I have mentioned in my journal and final document).

3. Start the server:

```
python App/Backend/app.py
```

4. Go to http://localhost:8000 ,follow the steps on the page, and enjoy the application!
