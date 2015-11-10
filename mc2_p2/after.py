#!/usr/bin/env python


import pandas as pd
import matplotlib.pyplot as plt
from util import get_data
from portfolio.analysis import get_portfolio_stats
from marketsim import compute_portvals
import scipy.optimize as spo


def plot(orders):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    prices.plot(ax=ax1)
    roc.plot(ax=ax2, label='ROC(1) on SMA(20)')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("% Change")
    for date, order in orders.iterrows():
        color = 'g' if order.ix['Order'] == 'BUY' else 'r'
        ax1.axvline(x=date, color=color)
        ax2.axvline(x=date, color=color)
    ax1.legend(loc=3)
    ax2.legend(loc=3)
    plt.show()


def generate_orders(signal_buffer=0.001):
    orders_list = []
    position = 0
    for date, sma_roc in roc[20:].iteritems():
        # trending up
        if sma_roc > signal_buffer and position <= 0:
            amount = 100 - position
            position = 100
            orders_list.append({
                'Date': date,
                'Symbol': symbol,
                'Order': 'BUY',
                'Shares': amount
            })
        # trending down
        if sma_roc < -signal_buffer and position >= 0:
            amount = abs(-100 - position)
            position = -100
            orders_list.append({
                'Date': date,
                'Symbol': symbol,
                'Order': 'SELL',
                'Shares': amount
            })
    if orders_list:
        return pd.DataFrame.from_records(orders_list, index='Date')


def test_strategy(signal_buffer):
    '''Optimization function'''
    orders = generate_orders(signal_buffer)
    if orders is None:
        cum_ret = (prices[symbol][-1] / prices[symbol][0]) - 1
    else:
        orders.to_csv(orders_file, columns=['Symbol', 'Order', 'Shares'],
                      index_label='Date')
        portvals = compute_portvals(start_date, end_date, orders_file, start_val)
        cum_ret, _, _, sharpe_ratio = get_portfolio_stats(portvals)
    return orders, cum_ret


def optimize():
    def func(args):
        _, cum_ret = test_strategy(args[0])
        return -cum_ret

    Xguess = [0.001]
    print spo.basinhopping(func, Xguess, stepsize=0.01, disp=True)


start_date = '2009-12-31'
end_date = '2011-12-31'
symbol = 'IBM'
orders_file = 'after-orders.csv'
start_val = 10000

dates = pd.date_range(start_date, end_date)
prices = get_data([symbol], dates)
prices.drop('SPY', axis=1, inplace=True)
prices['sma'] = pd.rolling_mean(prices, 15)
roc = (prices['sma'] / prices['sma'].shift(1)) - 1

orders, cum_ret = test_strategy(0.005)
plot(orders)
