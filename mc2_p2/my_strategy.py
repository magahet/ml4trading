"""MC2-P2: Kalman Strategy."""

import pandas as pd
import matplotlib.pyplot as plt
from util import get_data
import numpy as np


class Linear1DKalmanModel(object):
    '''1D linear Kalman model.'''

    def __init__(self):
        '''Set initial matrices.'''
        self.x = np.mat(
            [[0.], [0.], [0.], [0.]])  # initial state (value and velocity)
        self.P = np.mat([
            [1000., 0., 0., 0.],
            [0., 1000., 0., 0.],
            [0., 0., 1000., 0.],
            [0., 0., 0., 1000.]
        ])  # initial uncertainty
        self.Q = np.mat([
            [0., 0., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 0., 100.]
        ])  # initial uncertainty
        self.R = np.mat([[100.]])  # measurement uncertainty
        self.u = np.mat([[0.], [0.], [0.], [0.]])  # external motion; none
        dt = 1.
        self.F = np.mat([
            [1., dt, (dt ** 2) / 2, (dt ** 3) / 6],
            [0., 1, dt, (dt ** 2) / 2],
            [0., 0., 1., dt],
            [0, 0, 0, 1.]
        ])  # state transition function
        self.H = np.mat([[1., 0., 0., 0.]])  # measurement function
        self.I = np.mat(np.eye(4))  # 2d identity matrix
        self.current_value = self.x[0, 0]
        self.current_std = np.sqrt(self.P[0, 0])
        self.current_momentum = self.x[1, 0]
        self.predicted_value = self.x[0, 0]
        self.predicted_std = np.sqrt(self.P[0, 0])
        self.predicted_momentum = self.x[1, 0]

    def add_measurement(self, data_point):
        '''Add data point.'''
        # measurement update
        z = np.mat([[data_point]])
        y = z - (self.H * self.x)
        S = self.H * self.P * self.H.T + self.R
        K = self.P * self.H.T * S.I
        self.x = self.x + (K * y)
        self.P = (self.I - (K * self.H)) * self.P
        self.current_value = self.x[0, 0]
        self.current_std = np.sqrt(self.P[0, 0])
        self.current_mommentum = self.x[1, 0]
        # prediction
        self.x = (self.F * self.x) + self.u
        self.P = self.F * self.P * self.F.T + self.Q
        self.predicted_value = self.x[0, 0]
        self.predicted_std = np.sqrt(self.P[0, 0])
        self.predicted_mommentum = self.x[1, 0]


class KalmanTradingEngine(object):
    '''Trade recommendation engine based on kalman bands.'''

    def __init__(self, symbol, long_limit=None, short_limit=None, window=20):
        self.model = Linear1DKalmanModel()
        self.symbol = symbol
        self.long_limit = long_limit
        self.short_limit = short_limit
        self.current_position = 0
        self.history = pd.Series()
        self.smoothed = pd.Series()
        self.std = pd.Series()
        self.recommendation_history = pd.DataFrame(
            columns=['Symbol', 'Order', 'Shares'])

    def add_data_point(self, date, price):
        self.history = self.history.append(pd.Series({date: price}))
        self.model.add_measurement(price)
        self.smoothed = self.smoothed.append(
            pd.Series({date: self.model.current_value}))
        self.std = self.std.append(
            pd.Series({date: self.model.current_std}))

    def get_recommendation(self, velocity_threshold=0):
        '''Recommend whether to buy, sell, or hold.'''

        def is_rising():
            return self.model.current_mommentum > velocity_threshold

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

        def is_falling():
            return self.model.current_mommentum < -velocity_threshold

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

        current_date = self.history.index[-1]
        if is_rising() and can_buy():
            return buy()
        if is_falling() and can_sell():
            return sell()
        #if is_long_entry() and can_buy():
            #return buy()
        #elif is_short_entry() and can_sell():
            #return sell()
        #elif moved_above_sma() and can_exit_long():
            #return sell()
        #elif moved_below_sma() and can_exit_short():
            #return buy()
        return None

    def stats(self):
        return self.model.current_value, self.model.current.std

    def plot(self, title='', xlabel="Date", ylabel="Price"):
        """Plot stock prices with a custom title and meaningful axis labels."""
        upper_band = self.smoothed + 2 * self.std
        lower_band = self.smoothed - 2 * self.std
        fig, ax = plt.subplots()
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.plot(self.history.index, self.history, "b-", label=self.symbol)
        ax.plot(
            self.history.index, self.smoothed, "y-", label='Kalman Filtered')
        ax.plot(self.history.index, upper_band, "c-",
                label='Kalman Bollinger Bands')
        ax.plot(self.history.index, lower_band, "c-", label='')
        for date, recommendation in self.recommendation_history.iterrows():
            color = 'g' if recommendation.ix['Order'] == 'BUY' else 'r'
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
