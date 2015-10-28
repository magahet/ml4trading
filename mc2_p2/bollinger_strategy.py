"""MC1-P1: Analyze a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

from util import get_data, plot_data


def get_portfolio_value(prices, allocs, start_val=1):
    """Compute daily portfolio value given stock prices, allocations and starting value.

    Parameters
    ----------
        prices: daily prices for each stock in portfolio
        allocs: initial allocations, as fractions that sum to 1
        start_val: total starting value invested in portfolio (default: 1)

    Returns
    -------
        port_val: daily portfolio value
    """
    # TODO: Your code here
    #daily_returns = (prices / prices.shift(1)) - 1
    #daily_returns.ix[0, :] = 0
    normed = prices / prices.ix[0]
    alloced = normed * allocs
    pos_vals = alloced * start_val
    port_val = pos_vals.sum(axis=1)

    return port_val


def get_portfolio_stats(port_val, daily_rf=0, samples_per_year=252):
    """Calculate statistics on given portfolio values.

    Parameters
    ----------
        port_val: daily portfolio value
        daily_rf: daily risk-free rate of return (default: 0%)
        samples_per_year: frequency of sampling (default: 252 trading days)

    Returns
    -------
        cum_ret: cumulative return
        avg_daily_ret: average of daily returns
        std_daily_ret: standard deviation of daily returns
        sharpe_ratio: annualized Sharpe ratio
    """
    # TODO: Your code here
    cum_ret = (port_val[-1] / port_val[0]) - 1

    daily_ret = (port_val / port_val.shift(1)) - 1
    daily_ret = daily_ret[1:]

    avg_daily_ret = daily_ret.mean(axis=0)
    std_daily_ret = daily_ret.std(axis=0)
    sharpe_ratio = np.sqrt(samples_per_year) * (avg_daily_ret - daily_rf) / std_daily_ret
    return cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio


def plot_normalized_data(df, title="Normalized prices", xlabel="Date", ylabel="Normalized price"):
    """Normalize given stock prices and plot for comparison.

    Parameters
    ----------
        df: DataFrame containing stock prices to plot (non-normalized)
        title: plot title
        xlabel: X-axis label
        ylabel: Y-axis label
    """
    #TODO: Your code here
    df = df / df.ix[0, :]
    plot_data(df, title=title, xlabel=xlabel, ylabel=ylabel)


def assess_portfolio(start_date, end_date, symbols, allocs, start_val=1):
    """Simulate and assess the performance of a stock portfolio."""
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices = prices_all[symbols]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value
    port_val = get_portfolio_value(prices, allocs, start_val)
    #plot_data(port_val, title="Daily Portfolio Value")

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(port_val)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocs
    print "Sharpe Ratio:", sharpe_ratio
    print "Volatility (stdev of daily returns):", std_daily_ret
    print "Average Daily Return:", avg_daily_ret
    print "Cumulative Return:", cum_ret

    # Compare daily portfolio value with SPY using a normalized plot
    df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value and SPY")


class BollingerTradingEngine(object):
    '''Trade recommendation engine based on bollinger bands.'''

    def __init__(self, start_value=None, buy_limit=None, sell_limit=None, window=20):
        self.start_value = start_value
        self.buy_limit = buy_limit
        self.sell_limit = sell_limit
        self.window = window
        self.history = pd.Series()
        self.sma = None
        self.std = None

    def add_data_point(price):
        self.history.append(price)
        if len(history) >= self.window:
            self.sma = history.ix[-window:].mean(axis=0)
            self.std = history.ix[-window:].std(axis=0)

    def recommendation():
        if len(self.history) < 2 or not self.sma or not self.std:
            return None
        last_price = self.history[-2]
        current_price = self.history[-1]
        upper_band = self.sma + 2 * self.std
        lower_band = self.sma - 2 * self.std
        if last_price < lower_band and current_price > lower_band:
            return ('BUY', self.buy_limit)
        elif last_price > upper_band and current_price < upper_band:
            return ('SELL', self.sell_limit)


def run_bollinger():
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'

    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices_IBM = prices_all['IBM']  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    engine = BollingerTradingEngine(start_value=10000, buy_limit=100, sell_limit=100)
    for date, price in prices_IBM.iteritems():
        engine.add_data(date, price)
        print date, price, engine.recommendation()
    engine.plot()


if __name__ == "__main__":
    run_bollinger()
