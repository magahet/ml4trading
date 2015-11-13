#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import LinRegLearner as lrl
import KNNLearner as knn


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
    lrl_l = lrl.LinRegLearner()
    knn_l = knn.KNNLearner()
    lrl_l.addEvidence(trainX, trainY)  # train it
    knn_l.addEvidence(trainX, trainY)  # train it
    lrl_y = lrl_l.query(testX)  # get the predictions
    knn_y = knn_l.query(testX)  # get the predictions

    knn_df = pd.DataFrame({'x': testX[:, 0], 'y': knn_y})
    lrl_df = pd.DataFrame({'x': testX[:, 0], 'y': lrl_y})

    data = pd.DataFrame({'x': testX[:, 0], 'y': testY.flatten()})
    plot(data, knn_df, lrl_df)

    cor = pd.DataFrame({'actual': testY.flatten(), 'predicted': knn_y})
    cor.plot(kind='scatter', x='actual', y='predicted')
    plt.show()
