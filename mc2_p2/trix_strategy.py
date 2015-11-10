"""MC2-P2: TRIX Strategy."""

import pandas as pd
import matplotlib.pyplot as plt
from util import get_data
import collections
import numpy as np


class EMA(object):

    def __init__(self, periods):
        self.periods = periods
        self.history = []
        self.ema = np.nan
        self.multiplier = (2.0 / (periods + 1))

    def update(self, value):
        #print value, self.history, self.ema
        if value is None or value is np.nan:
            # invalid value
            pass
        elif self.ema is not np.nan:
            # update ema
            self.ema += (value - self.ema) * self.multiplier
        elif len(self.history) < self.periods - 1:
            # not enough data yet
            self.history.append(value)
        elif len(self.history) == self.periods - 1:
            # set ema to sma
            self.history.append(value)
            self.ema = np.mean(self.history)
        return self.ema

    @property
    def value(self):
        return self.ema


class ROC(object):

    def __init__(self, periods):
        self.history = collections.deque([], periods + 1)
        self.value = np.nan

    def update(self, value):
        if value and value is not np.nan:
            self.history.append(value)
            self.value = (self.history[-1] / self.history[0]) - 1
        return self.value


class SMA(object):

    def __init__(self, periods):
        self.history = collections.deque([], periods + 1)
        self.value = np.nan

    def update(self, value):
        if value and value is not np.nan:
            self.history.append(value)
        if len(self.history) == self.history.maxlen:
            self.value = np.mean(self.history)
        return self.value


class EMAROC(object):

    def __init__(self, ema_factor=1, ema_period=15, roc_period=1):
        self.ema_list = [EMA(ema_period) for _ in range(ema_factor)]
        self.roc = ROC(roc_period)

    def update(self, value):
        for ema in self.ema_list:
            value = ema.update(value)
        return self.roc.update(value)

    @property
    def value(self):
        return self.roc.value


class TRIXTradingEngine(object):
    '''Trade recommendation engine based on TRIX bands.'''

    def __init__(self, symbol, long_limit=None,
                 short_limit=None, smoothing=3, period=15, signal=9):
        self.symbol = symbol
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.history = pd.DataFrame(
            columns=[self.symbol, 'TRIX', 'EMA(9)'])
        self.trix = EMAROC(smoothing, period, 1)
        self.signal = SMA(signal)
        self.last_trix = self.trix.value
        self.last_signal = self.signal.value
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])

    def add_data_point(self, date, price):
        self.last_trix = self.trix.value
        self.last_signal = self.signal.value
        self.trix.update(price)
        self.signal.update(self.trix.value)
        df = pd.DataFrame(
            [[price, self.trix.value, self.signal.value]],
            columns=[self.symbol, 'TRIX', 'EMA(9)'],
            index=[date]
        )
        self.history = self.history.append(df)

    def get_recommendation(self):
        '''Recommend whether to buy, sell, or hold.'''

        def can_buy():
            return self.current_position < self.long_limit

        def buy():
            amount = self.long_limit - self.current_position
            self.current_position = self.long_limit
            recommendation = pd.DataFrame(
                [[self.symbol, 'BUY', amount]],
                columns=['Symbol', 'Order', 'Shares'],
                index=[current_date]
            )
            self.recommendation_history = self.recommendation_history.append(
                recommendation)
            return recommendation

        def can_sell():
            return self.current_position > self.short_limit

        def sell():
            amount = self.current_position - self.short_limit
            self.current_position = self.short_limit
            recommendation = pd.DataFrame(
                [[self.symbol, 'SELL', amount]],
                columns=['Symbol', 'Order', 'Shares'],
                index=[current_date]
            )
            self.recommendation_history = self.recommendation_history.append(
                recommendation)
            return recommendation

        def not_enough_data():
            return self.trix.value is np.nan

        def is_rising():
            #return self.trix.value > 0 and self.last_trix <= 0
            return (
                self.trix.value > self.signal.value and
                self.last_trix <= self.last_signal
            )

        def is_falling():
            #return self.trix.value < 0 and self.last_trix >= 0
            return (
                self.trix.value < self.signal.value and
                self.last_trix >= self.last_signal
            )

        if not_enough_data():
            return None
        current_date = self.history.index[-1]
        #print current_date, is_rising(), is_falling(), self.current_position
        if self.trix.value > 0 and can_buy():
            buy()
        elif self.trix.value < 0 and can_sell():
            sell()
        return None

    def stats(self):
        return self.ema_list, self.roc, self.history.size, self.trix, self.signal

    def plot(self, title='', xlabel="Date", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        #print self.history[['TRIX', 'EMA(9)']].applymap(np.isreal)
        #print self.history[['TRIX', 'EMA(9)']].tail()
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        self.history[self.symbol].plot(ax=ax1)
        df = self.history.loc[:, ['TRIX', 'EMA(9)']]
        df.plot(ax=ax2)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price")
        for date, recommendation in self.recommendation_history.iterrows():
            color = 'g' if recommendation.ix['Order'] == 'BUY' else 'r'
            ax1.axvline(x=date, color=color)
            ax2.axvline(x=date, color=color)
        ax1.legend(loc=3)
        plt.show()

    def create_order_book(self, path):
        self.recommendation_history.to_csv(
            path, columns=['Symbol', 'Order', 'Shares'], index_label='Date')


def run_TRIX(debug=False):
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    symbols = ['IBM']

    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices_IBM = prices_all['IBM']  # only portfolio symbols
    #prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    engine = TRIXTradingEngine('IBM', long_limit=100,
                               short_limit=-100)
    for date, price in prices_IBM.iteritems():
        engine.add_data_point(date, price)
        recommendation = engine.get_recommendation()
        if debug and recommendation is not None:
            print date, price, engine.stats()
            print recommendation
    engine.plot()
    engine.create_order_book('TRIX-orders.csv')


def test():
    d = EMAROC(1, 5, 1)
    for i in range(20):
        print d.update(i)

if __name__ == "__main__":
    run_TRIX()
    #test()
