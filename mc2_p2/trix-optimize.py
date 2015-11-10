import scipy.optimize as spo
from portfolio.analysis import get_portfolio_stats
from marketsim import compute_portvals
from trix_strategy import TRIXTradingEngine
from util import get_data
import pandas as pd


def find_optimal():
    """Find optimal allocations for a stock portfolio, optimizing for Sharpe ratio.

    Parameters
    ----------
        prices: daily prices for each stock in portfolio

    Returns
    -------
        allocs: optimal allocations, as fractions that sum to 1.0
    """

    # TODO: Your code here

    def fun(args):
        '''Optimization function'''
        smoothing, period, signal = (int(i) for i in args)
        engine = TRIXTradingEngine('IBM', long_limit=100,
                                   short_limit=-100, smoothing=smoothing,
                                   period=period, signal=signal)
        for date, row in prices.iterrows():
            engine.add_data_point(date, row['IBM'])
            engine.get_recommendation()
        engine.create_order_book(orders_file)
        portvals = compute_portvals(start_date, end_date, orders_file, start_val)
        cum_ret, _, _, _ = get_portfolio_stats(portvals)
        return -cum_ret

    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    symbols = ['IBM']
    start_val = 10000
    orders_file = 'trix-orders.csv'

    dates = pd.date_range(start_date, end_date)
    prices = get_data(symbols, dates)  # automatically adds SPY

    Xguess = [3, 15, 9]
    bnds = [(1, 4), (5, 30), (5, 15)]
    min_result = spo.minimize(fun, Xguess, method='SLSQP',
                              bounds=bnds, options={'disp': True})
    return min_result

if __name__ == '__main__':
    print find_optimal()
