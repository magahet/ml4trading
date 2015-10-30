"""MC2-P2: Bollinger Strategy."""

import pandas as pd
import matplotlib.pyplot as plt
from util import get_data


class BollingerTradingEngine(object):
    '''Trade recommendation engine based on bollinger bands.'''

    def __init__(self, symbol, start_value=None, long_limit=None,
                 short_limit=None, window=20):
        self.symbol = symbol
        self.start_value = start_value
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.window = window
        self.history = pd.Series()
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])
        self.sma = None
        self.std = None
        self.last_sma = None
        self.last_std = None

    def add_data_point(self, date, price):
        self.history = self.history.append(pd.Series({date: price}))
        if self.history.size >= self.window:
            self.last_sma = self.sma
            self.last_std = self.std
            self.sma = self.history.ix[-self.window:].mean(axis=0)
            self.std = self.history.ix[-self.window:].std(axis=0)

    def get_recommendation(self):
        '''Recommend whether to buy, sell, or hold.'''

        def is_long_entry():
            return (
                last_price <= self.last_sma - 2 * self.last_std and
                current_price > self.sma - 2 * self.std
            )

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

        def is_short_entry():
            return (
                last_price >= self.last_sma + 2 * self.last_std and
                current_price < self.sma + 2 * self.std
            )

        def can_sell():
            return self.current_position > self.short_limit

        def sell():
            self.current_position += self.short_limit
            recommendation = pd.DataFrame(
                [[self.symbol, 'SELL', abs(self.short_limit)]],
                columns=['Symbol', 'Order', 'Shares'],
                index=[current_date]
            )
            self.recommendation_history = self.recommendation_history.append(
                recommendation)
            return recommendation

        def not_enough_data():
            return (
                self.history.size < 2 or
                not all([self.sma, self.std, self.last_sma, self.last_std])
            )

        def moved_above_sma():
            return last_price <= self.last_sma and current_price > self.sma

        def moved_below_sma():
            return last_price >= self.last_sma and current_price < self.sma

        def can_exit_long():
            return self.current_position >= self.long_limit

        def can_exit_short():
            return self.current_position <= self.short_limit

        if not_enough_data():
            return None
        current_date = self.history.index[-1]
        last_price = self.history[-2]
        current_price = self.history[-1]
        if is_long_entry() and can_buy():
            return buy()
        elif is_short_entry() and can_sell():
            return sell()
        elif moved_above_sma() and can_exit_long():
            return sell()
        elif moved_below_sma() and can_exit_short():
            return buy()
        return None

    def stats(self):
        return self.sma, self.std, self.history.size, self.current_position

    def plot(self, title='', xlabel="Date", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        rolling_sma = pd.rolling_mean(self.history, self.window)
        rolling_std = pd.rolling_std(self.history, self.window)
        upper_band = rolling_sma + 2 * rolling_std
        lower_band = rolling_sma - 2 * rolling_std
        fig, ax = plt.subplots()
        fig.set_size_inches(8, 6, forward=True)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.plot(self.history.index, self.history, "b-", label=self.symbol)
        ax.plot(self.history.index, rolling_sma, "y-", label='SMA')
        ax.plot(self.history.index, upper_band, "c-", label='Bollinger Bands')
        ax.plot(self.history.index, lower_band, "c-", label='')
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

    engine = BollingerTradingEngine('IBM', start_value=10000, long_limit=100,
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
