"""MC2-P2: Bollinger Strategy."""

import pandas as pd
import matplotlib.pyplot as plt
from util import get_data
import collections
import numpy as np


class EMA(object):

    def __init__(self, periods):
        self.periods = periods
        self.history = []
        self.ema = None
        self.multiplier = (2.0 / (periods + 1))

    def update(self, value):
        if self.ema:
            # update ema
            self.ema += (value - self.ema) * self.multiplier
        elif value is None:
            # invalid value
            pass
        elif len(self.history) < self.periods:
            # not enough data yet
            self.history.append(value)
        else:
            # set ema to sma
            self.history.append(value)
            self.ema = np.mean(self.history)
        return self.ema

    def __repr__(self):
        return self.ema

    def __str__(self):
        return str(self.ema)


class ROC(object):

    def __init__(self, periods):
        self.history = collections.deque([], periods + 1)
        self.value = None

    def update(self, value):
        if value:
            self.history.append(value)
            self.value = self.history[-1] - self.history[0]
        return self.value

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)


class BollingerTradingEngine(object):
    '''Trade recommendation engine based on bollinger bands.'''

    def __init__(self, symbol, long_limit=None,
                 short_limit=None, period=15, signal=9):
        self.symbol = symbol
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.history = pd.DataFrame(
            columns=[self.symbol, 'TRIX', 'EMA(9)'])
        self.ema_list = [EMA(15), EMA(15), EMA(15)]
        self.trix = ROC(1)
        self.signal = EMA(9)
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])

    def add_data_point(self, date, price):
        value = price
        for index in range(len(self.ema_list)):
            value = self.ema_list[index].update(value)
        self.trix.update(value)
        self.signal.update(price)
        trix = self.trix if self.trix is not None else np.nan
        signal = self.signal if self.signal is not None else np.nan
        df = pd.DataFrame(
            [[price, trix, signal]],
            columns=[self.symbol, 'TRIX', 'EMA(9)'],
            index=[date]
        )
        self.history = self.history.append(df)

    def get_recommendation(self):
        '''Recommend whether to buy, sell, or hold.'''

        def can_buy():
            return self.current_position < self.long_limit

        def buy():
            self.current_position += self.long_limit
            recommendation = pd.DataFrame(
                [[self.symbol, 'BUY', self.long_limit]],
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
            return self.trix is not None

        if not_enough_data():
            return None
        current_date = self.history.index[-1]
        #if is_rising() and can_buy():
            #buy()
        #if is_falling() and can_sell():
            #sell()
        return None

    def stats(self):
        return self.ema_list, self.roc, self.history.size, self.trix, self.signal

    def plot(self, title='', xlabel="Date", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        print self.history
        ax = self.history.plot()
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        colors = {
            100: 'g',
            -100: 'r',
            0: 'k',
        }
        position = 0
        for date, recommendation in self.recommendation_history.iterrows():
            delta = 100 if recommendation.ix['Order'] == 'BUY' else -100
            position += delta
            color = colors.get(position, 'b')
            ax.axvline(x=date, color=color)
        ax.legend(loc=3)
        plt.show()

    def create_order_book(self, path):
        self.recommendation_history.to_csv(
            path, columns=['Symbol', 'Order', 'Shares'], index_label='Date')


def run_bollinger(debug=False):
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    symbols = ['IBM']

    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices_IBM = prices_all['IBM']  # only portfolio symbols
    #prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    engine = BollingerTradingEngine('IBM', long_limit=100,
                                    short_limit=-100)
    for date, price in prices_IBM.iteritems():
        engine.add_data_point(date, price)
        recommendation = engine.get_recommendation()
        if debug and recommendation is not None:
            print date, price, engine.stats()
            print recommendation
    engine.plot()
    engine.create_order_book('bollinger-orders.csv')


if __name__ == "__main__":
    run_bollinger()
