"""
Test a learner.  (c) 2015 Tucker Balch
"""

import numpy as np
import KNNLearner as knn


class BagLearner(object):

    def __init__(self, learner=knn.KNNLearner, kwargs=None, bags=20,
                 boost=False):
        '''Setup the learners.'''
        kwargs = {} if kwargs is None else kwargs
        self.learners = [learner(**kwargs) for _ in range(bags)]
        self.boost = boost

    def addEvidence(self, dataX, dataY):
        '''Train the learner with sample data.'''
        self.dataX = dataX
        self.dataY = dataY
        if self.boost:
            self.train_with_boosting()
        else:
            self.train()

    def query(self, points):
        '''Query the learner for estimates based on given data.'''
        estimates = []
        for learner in self.learners:
            estimates.append(learner.query(points))
        return np.array(estimates).mean(axis=0)

    def train(self):
        '''Train learners with simple bagging.'''
        for learner in self.learners:
            dataX_sampled, dataY_sampled = self.get_samples()
            learner.addEvidence(dataX_sampled, dataY_sampled)

    def get_samples(self, weights=None):
        '''Get samples from training data.'''
        sample_count = self.dataX.shape[0]
        indices = np.random.choice(np.arange(sample_count),
                                   size=sample_count,
                                   p=weights)
        return self.dataX[indices, :], self.dataY[indices]

    def train_with_boosting(self):
        '''Train learners with boosting.'''
        # Set uniform initial weights
        sample_count = self.dataX.shape[0]
        weights = np.ones(sample_count) / sample_count
        for index, learner in enumerate(self.learners):
            dataX_sampled, dataY_sampled = self.get_samples(weights)
            learner.addEvidence(dataX_sampled, dataY_sampled)

            # Test current learner with full data and get weights
            # Skip this if on the last learner
            if index < len(self.learners) - 1:
                instance_estimates = learner.query(self.dataX)
                weights = self.get_boosting_weights(instance_estimates)

    def get_boosting_weights(self, estimates):
        '''Get percentage histogram of estimate errors.'''
        absolute_error = np.abs(estimates - self.dataY)
        return absolute_error / absolute_error.sum()
