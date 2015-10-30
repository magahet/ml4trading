"""MC2-P2: Kalman Strategy."""

import pandas as pd
import matplotlib.pyplot as plt
from util import get_data
import numpy as np


class Linear1DKalmanModel(object):
    '''1D linear Kalman model.'''

    def __init__(self):
        '''Set initial matrices.'''
        self.x = np.mat([[0.], [0.]])  # initial state (value and velocity)
        self.P = np.mat([[1000., 0.], [0., 1000.]])  # initial uncertainty
        self.u = np.mat([[0.], [0.]])  # external motion; none
        self.F = np.mat([[1., 1.], [0, 1.]])  # state transition function
        self.H = np.mat([[1., 0.]])  # measurement function
        self.R = np.mat([[1.]])  # measurement uncertainty
        self.I = np.mat(np.identity(2))  # 2d identity matrix
        self.current_value = self.x[0, 0]
        self.current_uncertainty = self.P[0, 0]
        self.current_momentum = self.x[1, 0]
        self.predicted_value = self.x[0, 0]
        self.predicted_uncertainty = self.P[0, 0]
        self.predicted_momentum = self.x[1, 0]

    def add_measurement(self, data_point):
        '''Add data point.'''
        # measurement update
        z = np.mat([[data_point]])
        y = z - (self.H * self.x)
        S = self.H * self.P * self.H.transpose() + self.R
        K = self.P * self.H.transpose() * S.inverse()
        self.x = self.x + (K * y)
        self.P = (self.I - (K * self.H)) * self.P
        self.current_value = self.x[0, 0]
        self.current_uncertainty = self.P[0, 0]
        self.current_mommentum = self.x[1, 0]
        # prediction
        self.x = (self.F * self.x) + self.u
        self.P = self.F * self.P * self.F.transpose()
        self.predicted_value = self.x[0, 0]
        self.predicted_uncertainty = self.P[0, 0]
        self.predicted_mommentum = self.x[1, 0]


class KalmanTradingEngine(object):
    '''Trade recommendation engine based on kalman bands.'''

    def __init__(self, symbol, long_limit=None, short_limit=None, window=20):
        self.model = Linear1DKalmanModel()
        self.symbol = symbol
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])

    def add_data_point(self, date, price):
        self.model.add_measurement(price)

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
        ax.plot(self.history.index, upper_band, "c-", label='Kalman Bands')
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


def run_kalman(debug=False):
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    symbols = ['IBM']

    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices_IBM = prices_all['IBM']  # only portfolio symbols
    #prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    engine = KalmanTradingEngine('IBM', long_limit=100, short_limit=-100)
    for date, price in prices_IBM.iteritems():
        engine.add_data_point(date, price)
        recommendation = engine.get_recommendation()
        if debug and recommendation is not None:
            print date, price, engine.stats()
            print recommendation
    engine.plot()
    engine.create_order_book('kalman-orders.csv')


if __name__ == "__main__":
    run_kalman()
