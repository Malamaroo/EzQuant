# Backend

All the calculations, written in Python. Everything is saved as CSVs in the Data folder, and each file reads the user's portfolio from Data/Portfolio/portfolio.csv.

- **request_stock_data.py** (in Scripts) - pulls weekly prices and earnings for every stock with yfinance, and makes the full price history and P/E ratio files.
- **app.py** - the Flask server that connects the frontend to the other files. Parts of this were written by AI (marked #AI WRITTEN).
- **hedging.py** - builds a covariance matrix of the portfolio against every other stock, and recommends the stock with the most negative covariance.
- **optimiser.py** - uses PyPortfolioOpt to reweight the portfolio for the highest return at the user's chosen yearly risk.
- **backtest.py** - my own backtest engine. Runs the portfolio between two dates and compares it to the P/E strategy (buying the lowest P/E stock each week). The momentum strategy was never made.

One annoying thing: hedging.py and optimiser.py need a file that backtest.py makes, so they depend on it.
