"""MC2-P1: Market simulator."""

import pandas as pd
import sys
import os
import numpy as np

from util import (get_data, plot_data)
from portfolio.analysis import get_portfolio_value, get_portfolio_stats
#from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data


def compute_portvals(start_date, end_date, orders_file, start_val):
    """Compute daily portfolio value given a sequence of orders in a CSV file.

    Parameters
    ----------
        start_date: first date to track
        end_date: last date to track
        orders_file: CSV file to read orders from
        start_val: total starting cash available

    Returns
    -------
        portvals: portfolio value for each trading day from start_date to end_date (inclusive)
    """
    # TODO: Your code here
    orders = get_orders(orders_file)
    # Override start and end date with values in orders file
    #start_date = orders.index.min()
    #end_date = orders.index.max()
    symbols = list(orders['Symbol'].unique())
    prices = get_prices(symbols, start_date, end_date)
    trades = get_trades(orders, prices, start_date, end_date)
    while True:
        holdings = get_holdings(trades, prices, start_val)
        values = get_values(holdings, prices)
        leverage = get_leverage(values)
        leverage_delta = leverage.diff()
        over_leveraged_indexes = (
            leverage[leverage > 2.0].index &
            leverage_delta[leverage_delta > 0.0].index &
            trades[trades != 0.0].dropna(how='all').index
        )

        if len(over_leveraged_indexes) == 0:
            break
        #print 'Trade results in leverage > 2.0. Removing.'
        #print trades.loc[over_leveraged_indexes[0]]
        #print
        trades.loc[over_leveraged_indexes[0]] = 0.0
    portval = get_portval(values)
    return portval


def get_portval(values):
    '''Create daily total portfolio value.'''
    return values.sum(axis=1)


def get_values(holdings, prices):
    '''Create values dataframe with daily values for each symbol.'''
    return holdings * prices


def get_holdings(trades_without_cash, prices, start_val):
    '''Create holdings dataframe with daily positions for each symbol.'''
    trades = trades_without_cash.copy()
    trades['Cash'][0] += start_val
    return trades.cumsum(axis=0)


def get_leverage(holdings_row):
    '''Create leverage dataframe calculated from daily holdings.'''
    stocks = holdings_row.drop(['Cash'], axis=1)
    cash = holdings_row['Cash']
    a = stocks.abs().sum(axis=1)
    b = stocks.sum(axis=1) + cash
    return a / b


def get_trades(orders, prices, start_date, end_date):
    '''Create trades DF from orders.'''
    dt_start_date = pd.to_datetime(start_date)
    dt_end_date = pd.to_datetime(end_date)
    trades = clone_df(prices)
    for index, row in orders.iterrows():
        if index < dt_start_date or index > dt_end_date:
            print 'Order out of date range:', index
            continue
        symbol = row['Symbol']
        shares = row['Shares']
        # Reverse trade operation for Sell orders
        operator = 1 if row['Order'] == 'BUY' else -1
        #print index, symbol, shares, operator
        trades[symbol][index] += operator * shares
        #print symbol, index, prices[symbol][index]
        trades['Cash'][index] += -1 * operator * shares * prices[symbol][index]
    return trades


def get_orders(orders_file):
    '''Create orders dataframe from orders_file path.'''
    orders = pd.read_csv(orders_file, index_col='Date', parse_dates=True)
    orders.sort_index(inplace=True)
    return orders


def get_prices(symbols, start_date, end_date):
    '''Create prices dataframe from symbols and start/end dates.'''
    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices = prices_all[symbols]
    #prices['Cash'] = pd.Series(np.ones(len(prices)), index=prices.index)
    prices['Cash'] = 1.0
    return prices


def clone_df(original, fill=0.0):
    return pd.DataFrame(fill, index=original.index, columns=original.columns)


def plot_comparision(portfolio, benchmark):
    df = portfolio.to_frame()
    df = df.join(benchmark)
    df = df.rename(columns={'$SPX': 'SPX', 0: 'Portfolio'})
    df = df / df.ix[0, :]
    plot_data(df, title='Daily portfolio value', ylabel='Normalized price')


def test_run(start_date, end_date, orders_file, start_val=1000000):
    """Driver function."""

    # Process orders
    portvals = compute_portvals(start_date, end_date, orders_file, start_val)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # if a DataFrame is returned select the first column to get a Series

    # Get portfolio stats
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(
        portvals)

    # Simulate a $SPX-only reference portfolio to get stats
    prices_SPX = get_data(['$SPX'], pd.date_range(start_date, end_date))
    prices_SPX = prices_SPX[['$SPX']]  # remove SPY
    portvals_SPX = get_portfolio_value(prices_SPX, [1.0])
    cum_ret_SPX, avg_daily_ret_SPX, std_daily_ret_SPX, sharpe_ratio_SPX = get_portfolio_stats(portvals_SPX)

    plot_comparision(portvals, prices_SPX)

    # Compare portfolio against $SPX
    print "Data Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of $SPX: {}".format(sharpe_ratio_SPX)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of $SPX: {}".format(cum_ret_SPX)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of $SPX: {}".format(std_daily_ret_SPX)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of $SPX: {}".format(avg_daily_ret_SPX)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

    # Plot computed daily portfolio value
    #df_temp = pd.concat(
        #[portvals, prices_SPX['$SPX']], keys=['Portfolio', '$SPX'], axis=1)
    #plot_normalized_data(df_temp, title="Daily portfolio value and $SPX")


def test_leverage_suite():
    '''Run set of leverage tests.

    Copied with permission from https://piazza.com/class/idadrtx18nie1?cid=518
    '''
    ordersFile = os.path.join('orders', 'leverageTest1.csv')
    leo_tester(
        startDate='2011-01-03', endDate='2011-12-14', ordersFile=ordersFile)
    ordersFile = os.path.join('orders', 'leverageTest2.csv')
    leo_tester(
        startDate='2011-01-03', endDate='2011-12-14', ordersFile=ordersFile)
    ordersFile = os.path.join('orders', 'leverageTest3.csv')
    leo_tester(
        startDate='2011-01-03', endDate='2011-12-14', ordersFile=ordersFile)


def leo_tester(startDate, endDate, ordersFile, resultsFile=None):
    ''' Enhanced testing funtion. Mostly works the same as Tucker's... but it's way better

    Copied with permission from https://piazza.com/class/idadrtx18nie1?cid=518

    Parameters
    ----------
        startDate: (str) first date to track
        endDate: (str) last date to track
        ordersFile: (str) CSV file to read orders from, ACTUALLY THIS REQUIRES A PATH
        resultsFile: (str) filepath for saving down answers, defaults to None

    Returns
    -------
        None
    '''
    start_val = 1000000
    # Process orders
    portvals = compute_portvals(startDate, endDate, ordersFile, start_val)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # if a DataFrame is returned select the first column to get a Series
    # Get portfolio stats
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(
        portvals)

    if resultsFile is not None:
        portvals.to_csv(resultsFile)

    #check answers
    if ordersFile == os.path.join('orders', 'leverageTest1.csv'):
        ansFile = os.path.join('orders', 'leverageTest1_ans.csv')
        testVsAnswer(portvals, ansFile, ordersFile)
    elif ordersFile == os.path.join('orders', 'leverageTest2.csv'):
        ansFile = os.path.join('orders', 'leverageTest2_ans.csv')
        testVsAnswer(portvals, ansFile, ordersFile)
    elif ordersFile == os.path.join('orders', 'leverageTest3.csv'):
        ansFile = os.path.join('orders', 'leverageTest3_ans.csv')
        testVsAnswer(portvals, ansFile, ordersFile)


def testVsAnswer(portvals, ansFile, ordersFile):
    ''' Testing file for individual answers, tries to tell you what you got wrong

    Copied with permission from https://piazza.com/class/idadrtx18nie1?cid=518

    Parameters
    ----------
        portvals: (pd.Series) portfolio values series
        ansFile: (str) CSV file path to read answers from
        ordersFile: (str) CSV file path to read orders from,

    Returns
    -------
        None
    '''
    print '*****************************************'
    print '   Testing %s' % ordersFile
    ansSeries = pd.Series.from_csv(ansFile)
    shapeEqual = portvals.shape == ansSeries.shape
    if not shapeEqual:
        print '******* ERROR in test: %s ********' % ordersFile
        print '    user answer: %s' % portvals.shape
        print '    target answer: %s' % ansSeries.shape
    else:
        ax = ansSeries.plot(label='answer')
        portvals.plot(ax=ax, linestyle='--', label='user', color='r')
        ax.set_title('Test for %s' % ordersFile)
        ax.legend()
        from matplotlib import pyplot as plt
        plt.show()
        try:
            np.testing.assert_array_almost_equal(
                portvals.values, ansSeries.values, decimal=4)
            print '****** SUCCESS!  CONGRATULATIONS! *******'
        except:
            print '******* ERROR in test: %s ********' % ordersFile
            print '    see graphs to debug'
    return None


def test_short():
    start_date = '2011-1-05'
    end_date = '2011-1-20'
    orders_file = 'orders/orders-short.csv'
    start_val = 1000000
    test_run(start_date, end_date, orders_file, start_val)


def test_orders():
    start_date = '2011-1-10'
    end_date = '2011-12-20'
    orders_file = 'orders/orders.csv'
    start_val = 1000000
    test_run(start_date, end_date, orders_file, start_val)


def test_leverage():
    start_date = '2011-1-10'
    end_date = '2011-12-20'
    orders_file = 'orders/leverage.csv'
    start_val = 1000000
    test_run(start_date, end_date, orders_file, start_val)


def test_leverage3():
    start_date = '2011-1-05'
    end_date = '2011-2-23'
    orders_file = 'orders/leverage3.csv'
    start_val = 1000000
    test_run(start_date, end_date, orders_file, start_val)


def test_orders2():
    start_date = '2011-1-14'
    end_date = '2011-12-14'
    orders_file = 'orders/orders2.csv'
    start_val = 1000000
    test_run(start_date, end_date, orders_file, start_val)


def test_bollinger():
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    orders_file = 'bollinger-orders.csv'
    start_val = 10000
    test_run(start_date, end_date, orders_file, start_val)


def test():
    start_date = '2005-12-31'
    end_date = '2011-12-31'
    orders_file = 'after-orders.csv'
    start_val = 10000
    test_run(start_date, end_date, orders_file, start_val)


if __name__ == "__main__":
    #locals()['test_' + sys.argv[1]]()
    test()
