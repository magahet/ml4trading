"""MC2-P2: Bollinger Strategy."""

import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import get_data


class BollingerBand(object):

    def __init__(self, periods):
        self.history = collections.deque([], periods + 1)
        self.sma = np.nan
        self.std = np.nan

    def update(self, value):
        if value and value is not np.nan:
            self.history.append(value)
        if self.has_enough_data():
            self.sma = np.mean(self.history)
            self.std = np.std(self.history)

    @property
    def upper(self):
        return self.sma + 2 * self.std

    @property
    def lower(self):
        return self.sma - 2 * self.std

    def has_enough_data(self):
        return len(self.history) == self.history.maxlen

    def percent_b(self, price):
        return (price - self.lower) / (self.upper - self.lower)


class BollingerDeltaTradingEngine(object):
    '''Trade recommendation engine based on bollinger bands.'''

    def __init__(self, symbol, signal_symbol='SPY', long_limit=None,
                 short_limit=None, window=20):
        self.symbol = symbol
        self.signal_symbol = signal_symbol
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.history = pd.DataFrame()
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])
        self.bollinger = BollingerBand(window)
        self.signal = BollingerBand(window)
        self.current_data = None
        self.current_price = np.nan
        self.current_signal_price = np.nan

    def add_data_point(self, date, price, signal_price):
        self.current_date = date
        self.current_price = price
        self.current_signal_price = signal_price
        self.bollinger.update(price)
        self.signal.update(signal_price)
        percent_b = self.bollinger.percent_b(price)
        signal_percent_b = self.signal.percent_b(signal_price)
        data = [
            price,
            self.bollinger.sma,
            self.bollinger.upper,
            self.bollinger.lower,
            percent_b,
            signal_percent_b,
        ]
        columns = [
            self.symbol,
            'SMA',
            'Upper Bollinger',
            'Lower Bollinger',
            '%b',
            'Signal %b',
        ]
        df = pd.DataFrame(
            [data],
            columns=columns,
            index=[date]
        )
        self.history = self.history.append(df)

    def get_recommendation(self, signal_buffer=0.0):
        '''Recommend whether to buy, sell, or hold.'''

        def trade(order, amount):
            recommendation = pd.DataFrame(
                [[self.symbol, order.upper(), amount]],
                columns=['Symbol', 'Order', 'Shares'],
                index=[self.current_date]
            )
            print recommendation
            print self.current_position, percent_b, signal_percent_b
            self.recommendation_history = self.recommendation_history.append(
                recommendation)

        def can_buy():
            return self.current_position < self.long_limit

        def can_sell():
            return self.current_position > self.short_limit

        def buy(all_in=False):
            if all_in:
                amount = self.long_limit - self.current_position
                self.current_position = self.long_limit
            else:
                amount = self.long_limit
                self.current_position += self.long_limit
            trade('BUY', amount)

        def sell(all_in=False):
            if all_in:
                amount = self.current_position - self.short_limit
                self.current_position = self.short_limit
            else:
                amount = abs(self.short_limit)
                self.current_position += self.short_limit
            trade('SELL', amount)

        def exit():
            if self.current_position != 0:
                self.current_position = 0
                order = 'BUY' if self.current_position < 0 else 'SELL'
                trade(order, -self.current_position)

        if not self.bollinger.has_enough_data():
            return None
        percent_b = self.bollinger.percent_b(self.current_price)
        signal_percent_b = self.bollinger.percent_b(self.current_signal_price)

        if False:
            pass
        #if abs(percent_b - signal_percent_b) > 0.5:
            #if can_buy() and percent_b < signal_percent_b:
                #buy(all_in=True)
            #if can_sell() and percent_b > signal_percent_b:
                #sell(all_in=True)
        #elif abs(percent_b - signal_percent_b) < 0.2:
            #if can_buy() and percent_b < signal_percent_b:
                #buy()
            #if can_sell() and percent_b > signal_percent_b:
                #sell()
        elif percent_b > 1.0 and can_sell():
            sell(all_in=True)
        elif percent_b < 0.0 and can_buy():
            buy(all_in=True)
        elif percent_b < 0.5 and self.current_position < 0:
            exit()
        elif percent_b > 0.5 and self.current_position > 0:
            exit()

    def plot(self, title='', xlabel="Date", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        print self.history
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        plot1_columns = [
            self.symbol,
            'SMA',
            'Upper Bollinger',
            'Lower Bollinger'
        ]
        self.history.loc[:, plot1_columns].plot(ax=ax1)
        plot2_columns = [
            '%b',
            'Signal %b'
        ]
        self.history.loc[:, plot2_columns].plot(ax=ax2)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price")
        colors = {
            100: 'g',
            -100: 'r',
            0: 'k',
        }
        position = 0
        for date, recommendation in self.recommendation_history.iterrows():
            delta = recommendation.ix['Shares']
            if recommendation.ix['Order'] == 'BUY':
                position += delta
            else:
                position -= delta
            #print position
            color = colors.get(position, 'b')
            ax1.axvline(x=date, color=color)
            ax2.axvline(x=date, color=color)
        #ax.legend(loc=3)
        plt.show()

    def create_order_book(self, path):
        self.recommendation_history.to_csv(
            path, columns=['Symbol', 'Order', 'Shares'], index_label='Date')


def run_bollinger_delta(debug=False):
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    symbols = ['IBM']

    dates = pd.date_range(start_date, end_date)
    prices = get_data(symbols, dates)  # automatically adds SPY
    #prices_IBM = prices_all['IBM']  # only portfolio symbols
    #prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    engine = BollingerDeltaTradingEngine('IBM', long_limit=100,
                                         short_limit=-100)
    for date, row in prices.iterrows():
        engine.add_data_point(date, row['IBM'], row['SPY'])
        engine.get_recommendation()
    engine.plot()
    engine.create_order_book('bollinger-delta-orders.csv')


if __name__ == "__main__":
    run_bollinger_delta()
