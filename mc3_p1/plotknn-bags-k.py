#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
#import LinRegLearner as lrl
import KNNLearner as knn
import BagLearner as bl


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
    rmse_train_list = []
    rmse_test_list = []
    b_list = range(1, 20)
    for b in b_list:
        learner = bl.BagLearner(learner=knn.KNNLearner, bags=b, kwargs={'k': 1})
        learner.addEvidence(trainX, trainY)  # train it
        predY = learner.query(trainX)  # get the predictions
        rmse_train = math.sqrt(((trainY - predY) ** 2).sum() / trainY.shape[0])
        rmse_train_list.append(rmse_train)
        predY = learner.query(testX)  # get the predictions
        rmse_test = math.sqrt(((testY - predY) ** 2).sum() / testY.shape[0])
        rmse_test_list.append(rmse_test)
        print b, rmse_train, rmse_test

    rmse = pd.DataFrame({'Train': rmse_train_list, 'Test': rmse_test_list},
                        index=b_list)
    #cc = pd.DataFrame({'Train': cc_train, 'Test': cc_test})
    rmse.plot()
    plt.tight_layout()
    #plt.gca().invert_xaxis()
    plt.xlabel('bags')
    plt.ylabel('rmse')
    plt.show()
