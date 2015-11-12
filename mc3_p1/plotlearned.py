#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import LinRegLearner as lrl
import KNNLearner as knn


def plot(data, knn, lnl):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    data.plot(kind='scatter', x='x', y='y', ax=ax1)
    knn.plot(kind='scatter', x='x', y='y', ax=ax2)
    lnl.plot(kind='scatter', x='x', y='y', ax=ax3)
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
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
    testX = data[:, 0:-1]

    # create a learner and train it
    lrl_l = lrl.LinRegLearner()
    knn_l = knn.KNNLearner()
    lrl_l.addEvidence(trainX, trainY)  # train it
    knn_l.addEvidence(trainX, trainY)  # train it
    lrl_y = lrl_l.query(testX)  # get the predictions
    knn_y = knn_l.query(testX)  # get the predictions

    data = pd.DataFrame(data, columns=['x', 'y'])
    plt.show()
