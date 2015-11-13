#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import time
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
    times = []
    b_list = range(10, 101, 10)
    for b in b_list:
        start = time.time()
        learner = bl.BagLearner(learner=knn.KNNLearner, bags=b)
        learner.addEvidence(trainX, trainY)  # train it
        predY = learner.query(trainX)  # get the predictions
        predY = learner.query(testX)  # get the predictions
        elapsed = time.time() - start
        times.append(elapsed)
        print b, elapsed

    rmse = pd.DataFrame({'Run Time': times},
                        index=b_list)
    #cc = pd.DataFrame({'Train': cc_train, 'Test': cc_test})
    rmse.plot()
    plt.tight_layout()
    #plt.gca().invert_xaxis()
    plt.xlabel('bags')
    plt.ylabel('time (sec)')
    plt.show()
