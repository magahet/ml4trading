#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import LinRegLearner as lrl
import KNNLearner as knn
import BagLearner as bl
from util import get_data
import argparse


def plot_orders(orders, prices, predY, indices):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    prices.plot(ax=ax1)
    predYDF = pd.DataFrame()
    predYDF['Predicted 5-day Price Change'] = pd.Series(predY, index=indices, copy=True)
    predYDF.plot(ax=ax2)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Forecast Price Change")
    colors = {
        100: 'g',
        -100: 'r',
        0: 'k',
    }
    position = 0
    for date, order in orders.iterrows():
        delta = order.ix['Shares']
        delta = -delta if order.ix['Order'] == 'SELL' else delta
        position += delta
        color = colors.get(position, 'b')
        ax1.axvline(x=date, color=color)
        ax2.axvline(x=date, color=color)
    ax1.legend(loc=3)
    ax2.legend(loc=3)
    plt.show()


def normalize(data, new_max=1, new_min=-1):
    old_min = data.min(axis=0)
    old_range = data.max(axis=0) - old_min
    new_range = new_max - new_min
    norm = lambda v: (((v - old_min) * new_range) / old_range) + new_min
    return data.apply(norm, axis=1)


def get_bb_value(price):
    sma = pd.rolling_mean(price, 20)
    stdev = pd.rolling_std(price, 20)
    return (price - sma) / (2 * stdev)


def get_momentum(price, n=5):
    return (price / price.shift(n)) - 1


def get_volatility(price):
    return pd.rolling_std(price, 20)


def get_price_change(price, n=5):
    return (price.shift(-n) / price) - 1


def setup_learner(args):
    learners = {
        'linreg': {
            'class': lrl.LinRegLearner,
            'kwargs': {},
        },
        'knn': {
            'class': knn.KNNLearner,
            'kwargs': {
                'k': args.k
            },
        }
    }

    if args.bagging:
        learner_class = learners.get(args.learner, {}).get('class')
        kwargs = learners.get(args.learner, {}).get('kwargs')
        learner = bl.BagLearner(learner=learner_class,
                                kwargs=kwargs,
                                bags=args.bags)
    else:
        learner_class = learners.get(args.learner, {}).get('class')
        kwargs = learners.get(args.learner, {}).get('kwargs')
        learner = learner_class(**kwargs)
    return learner


def parse_args():
    parser = argparse.ArgumentParser(description='Test Learners')
    parser.add_argument('learner', choices=['linreg', 'knn'],
                        help='learner to test')
    parser.add_argument('start_date', help='Start Date')
    parser.add_argument('end_date', help='End Date')
    parser.add_argument('symbol', help='Symbol')
    parser.add_argument('-k', default=3, type=int, help='K to use for KNN.')
    parser.add_argument('-b', '--bagging', default=False, action='store_true',
                        help='use bagging.')
    parser.add_argument('-n', '--bags', type=int, default=20,
                        help='number of bags to use in bagging.')
    parser.add_argument('-o', '--orders', default='orders.csv',
                        help='filename of orders file to create.')
    parser.add_argument('-S', '--start-test', dest='start_test',
                        help='Start Date of test')
    parser.add_argument('-E', '--end-test', dest='end_test',
                        help='End Date of test')
    return parser.parse_args()


def get_learning_data(start_date, end_date, symbol):
    dates = pd.date_range(start_date, end_date)
    prices = get_data([symbol], dates)
    prices.drop('SPY', axis=1, inplace=True)

    x_df = pd.DataFrame(index=prices.index)
    x_df['bb'] = get_bb_value(prices)
    x_df['momentum'] = get_momentum(prices)
    x_df['volatility'] = get_volatility(prices)
    x_df = normalize(x_df)
    y_values = get_price_change(prices, 5)

    indices = x_df.ix[19:-5].index
    x_df = x_df.ix[19:-5].values
    y_values = y_values.ix[19:-5, 0].values
    return prices, x_df, y_values, indices


def get_rmse(actual, predicted):
    return np.sqrt(((actual - predicted) ** 2).sum() / actual.shape[0])


def get_correlation(actual, predicted):
    c = np.corrcoef(predicted, y=actual)
    return c[0, 1]


def get_future_prices(prices, actualY, predY, indices):
    symbol = prices.columns[0]
    df = prices.copy()
    df['Train Y'] = pd.Series(actualY, index=indices, copy=True)
    df['Predicted Y'] = pd.Series(predY, index=indices, copy=True)
    df['Train Y'] = df[symbol] * (1 + df['Train Y'])
    df['Predicted Y'] = df[symbol] * (1 + df['Predicted Y'])
    return df


def plot_Y(prices, actualY, predY, indices, title=''):
    symbol = prices.columns[0]
    df = prices.copy()
    df['Train Y'] = pd.Series(actualY, index=indices, copy=True)
    df['Predicted Y'] = pd.Series(predY, index=indices, copy=True)
    df['Train Y'] = df[symbol] * (1 + df['Train Y'])
    df['Predicted Y'] = df[symbol] * (1 + df['Predicted Y'])
    ax = df.plot(title=title)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    plt.show()
    return df


def get_positions(predY, indicies, threshold=0.01):
    pos = pd.Series(predY, index=indicies, copy=True)
    pos[pos > threshold] = 1.0
    pos[pos < -threshold] = -1.0
    pos[(pos <= threshold) & (pos >= -threshold)] = 0.0
    return pos


def get_trades(pos):
    trades = pos - pos.shift(1)
    trades[0] = pos[0]
    return trades[trades != 0]


def generate_orders(symbol, trades, max_pos=100):
    orders_list = []
    for date, trade in trades.iteritems():
        order = 'BUY' if trade > 0 else 'SELL'
        amount = abs(trade) * max_pos
        orders_list.append({
            'Date': date,
            'Symbol': symbol,
            'Order': order,
            'Shares': amount
        })
    if orders_list:
        return pd.DataFrame.from_records(orders_list, index='Date')


def create_orders_file(orders, orders_file='orders.csv'):
    orders.to_csv(orders_file, columns=['Symbol', 'Order', 'Shares'],
                  index_label='Date')


if __name__ == '__main__':
    args = parse_args()
    prices, trainX, trainY, indices = get_learning_data(args.start_date,
                                                        args.end_date,
                                                        args.symbol)

    # create a learner and train it
    learner = setup_learner(args)
    learner.addEvidence(trainX, trainY)  # train it

    # evaluate in sample
    predY = learner.query(trainX)  # get the predictions
    rmse = get_rmse(trainY, predY)
    corr = get_correlation(trainY, predY)
    print
    print "In sample results"
    print "RMSE: ", rmse
    print "corr: ", corr
    plot_Y(prices, trainY, predY, indices,
           'Actual Y/Price/Predicted Y - {}'.format(args.symbol))

    positions = get_positions(predY, indices)
    trades = get_trades(positions)
    orders = generate_orders(args.symbol, trades)
    create_orders_file(orders, 'train-{}'.format(args.orders))
    plot_orders(orders, prices, predY, indices)

    if args.start_test and args.end_test:
        # evaluate out sample
        prices, testX, testY, indices = get_learning_data(args.start_test,
                                                          args.end_test,
                                                          args.symbol)
        predY = learner.query(testX)  # get the predictions
        rmse = get_rmse(testY, predY)
        corr = get_correlation(testY, predY)
        print
        print "In sample results"
        print "RMSE: ", rmse
        print "corr: ", corr

        #plot_Y(prices, testY, predY, indices,
            #'Actual Y/Price/Predicted Y - {}'.format(args.symbol)
        positions = get_positions(predY, indices)
        trades = get_trades(positions)
        orders = generate_orders(args.symbol, trades)
        create_orders_file(orders, 'test-{}'.format(args.orders))
        plot_orders(orders, prices, predY, indices)
