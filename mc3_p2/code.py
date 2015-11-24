#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import LinRegLearner as lrl
import KNNLearner as knn
import BagLearner as bl
from util import get_data
import argparse


def plot(data, knn_df, lnl_df):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    data.plot(kind='scatter', x='x', y='y', ax=ax1)
    knn_df.plot(kind='scatter', x='x', y='y', ax=ax2)
    lnl_df.plot(kind='scatter', x='x', y='y', ax=ax3)
    ax1.set_title('Actual')
    ax2.set_title('KNN')
    ax3.set_title('LinReg')
    plt.tight_layout()
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
    parser.add_argument('-s', '--start', default='10000',
                        help='Start value of portfolio')
    return parser.parse_args()


def get_training_data(start_date, end_date, symbol):
    dates = pd.date_range(start_date, end_date)
    prices = get_data([symbol], dates)
    prices.drop('SPY', axis=1, inplace=True)

    trainX = pd.DataFrame(index=prices.index)
    trainX['bb'] = get_bb_value(prices)
    trainX['momentum'] = get_momentum(prices)
    trainX['volatility'] = get_volatility(prices)
    trainX = normalize(trainX)
    trainY = get_price_change(prices, 5)

    indecies = trainX.ix[19:-5].index
    trainX = trainX.ix[19:-5].values
    trainY = trainY.ix[19:-5, 0].values
    return prices, trainX, trainY, indecies


def get_rmse(actual, predicted):
    return np.sqrt(((actual - predicted) ** 2).sum() / actual.shape[0])


def get_correlation(actual, predicted):
    c = np.corrcoef(predicted, y=actual)
    return c[0, 1]


def plot_Y(prices, actualY, predY, indecies):
    df = prices.copy()
    df['Train Y'] = pd.Series(actualY, index=indecies)
    df['Predicted Y'] = pd.Series(predY, index=indecies)
    df.plot()
    plt.show()


if __name__ == '__main__':
    args = parse_args()
    prices, trainX, trainY, indecies = get_training_data(args.start_date,
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

    plot_Y(prices, trainY, predY, indecies)

    # evaluate out of sample
    #predY = learner.query(testX)  # get the predictions
    #rmse = math.sqrt(((testY - predY) ** 2).sum() / testY.shape[0])
    #print
    #print "Out of sample results"
    #print "RMSE: ", rmse
    #c = np.corrcoef(predY, y=testY)
    #print "corr: ", c[0, 1]
