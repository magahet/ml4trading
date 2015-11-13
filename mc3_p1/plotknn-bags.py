#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
#import LinRegLearner as lrl
#import KNNLearner as knn
import BagLearner as bl


def plot(rmse, cc):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    rmse.plot(ax=ax1)
    cc.plot(ax=ax2)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    with open(sys.argv[1]) as inf:
        data = np.array(
            [map(float, s.strip().split(',')) for s in inf.readlines()])

    # compute how much of the data is training and testing
    train_rows = math.floor(0.6 * data.shape[0])
    test_rows = data.shape[0] - train_rows

    # separate out training and testing data
    trainX = data[:train_rows, 0:-1]
    trainY = data[:train_rows, -1]
    if len(sys.argv) > 2 and sys.argv[2] == 'all':
        testX = data[:, 0:-1]
        testY = data[:, -1]
    else:
        testX = data[train_rows:, 0:-1]
        testY = data[train_rows:, -1]

    # create a learner and train it
    rmse_train = []
    rmse_test = []
    cc_train = []
    cc_test = []
    for bags in xrange(10, 1001, 10):
        learner = bl.BagLearner(bags=bags)
        learner.addEvidence(trainX, trainY)  # train it

        # train set
        predY = learner.query(trainX)  # get the predictions
        rmse_train.append(math.sqrt(((trainY - predY) ** 2).sum() / trainY.shape[0]))
        c = np.corrcoef(predY, y=trainY)
        cc_train.append(c[0, 1])

        # test set
        predY = learner.query(testX)  # get the predictions
        rmse_test.append(math.sqrt(((testY - predY) ** 2).sum() / testY.shape[0]))
        c = np.corrcoef(predY, y=testY)
        cc_test.append(c[0, 1])

    rmse = pd.DataFrame({'Train': rmse_train, 'Test': rmse_test})
    cc = pd.DataFrame({'Train': cc_train, 'Test': cc_test})
    plot(rmse, cc)
