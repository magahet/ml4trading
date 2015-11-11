#!/usr/bin/env python
"""
Test a learner.  (c) 2015 Tucker Balch
"""

import numpy as np
import math
import LinRegLearner as lrl
import KNNLearner as knn
import BagLearner as bl

import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Learners')
    parser.add_argument('learner', choices=['linreg', 'knn'],
                        help='learner to test')
    parser.add_argument('-d', '--dataset-path', dest='dataset_path',
                        default='Data/ripple.csv', help='path to dataset file.')
    parser.add_argument('-k', default=3, help='K to use for KNN.')
    parser.add_argument('-b', '--bagging', default=False, action='store_true',
                        help='use bagging.')
    parser.add_argument('-n', '--bags', default=20,
                        help='number of bags to use in bagging.')
    parser.add_argument('-a', '--boost', default=False, action='store_true',
                        help='use boosting in bagging.')
    args = parser.parse_args()

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
                                bags=args.bags,
                                boost=args.boost)
    else:
        learner_class = learners.get(args.learner, {}).get('class')
        kwargs = learners.get(args.learner, {}).get('kwargs')
        learner = learner_class(**kwargs)

    with open(args.dataset_path) as inf:
        data = np.array(
            [map(float, s.strip().split(',')) for s in inf.readlines()])

    # compute how much of the data is training and testing
    train_rows = math.floor(0.6 * data.shape[0])
    test_rows = data.shape[0] - train_rows

    # separate out training and testing data
    trainX = data[:train_rows, 0:-1]
    trainY = data[:train_rows, -1]
    testX = data[train_rows:, 0:-1]
    testY = data[train_rows:, -1]

    # create a learner and train it
    learner.addEvidence(trainX, trainY)  # train it

    # evaluate in sample
    predY = learner.query(trainX)  # get the predictions
    rmse = math.sqrt(((trainY - predY) ** 2).sum() / trainY.shape[0])
    print
    print "In sample results"
    print "RMSE: ", rmse
    c = np.corrcoef(predY, y=trainY)
    print "corr: ", c[0, 1]

    # evaluate out of sample
    predY = learner.query(testX)  # get the predictions
    rmse = math.sqrt(((testY - predY) ** 2).sum() / testY.shape[0])
    print
    print "Out of sample results"
    print "RMSE: ", rmse
    c = np.corrcoef(predY, y=testY)
    print "corr: ", c[0, 1]
