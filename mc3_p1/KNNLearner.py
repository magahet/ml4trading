"""
A simple wrapper for linear regression.  (c) 2015 Tucker Balch
"""

import numpy as np
import scipy.spatial


class KNNLearner(object):

    def __init__(self, k=1):
        self.k = k

    def addEvidence(self, dataX, dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        #self.spatial_db = BruteSpatial(dataX)
        self.spatial_db = KDTree(dataX)
        self.dataY = dataY

    def query(self, points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        estimates = []
        for point in points:
            indices = self.spatial_db.search(point, k=self.k, indecies=True)
            estimates.append(self.dataY[indices].mean())
        return np.array(estimates)


class KDTree(object):
    '''Implements a kdtree spatial data structure.'''

    def __init__(self, points):
        self.kdtree = scipy.spatial.KDTree(points)

    def search(self, point, k=1, indecies=False):
        results = self.kdtree.query(point, k=k)
        if indecies:
            return results[1]
        else:
            return self.dktree.data[results[1]]


class BruteSpatial(object):
    '''Implements a naive spatial data structure.'''

    def __init__(self, points):
        self.points = points

    def search(self, point, k=1, indecies=False):
        '''Perform brute force knn search.'''
        if k >= self.points.shape[0]:
            if indecies:
                return np.arange(self.points.shape[0])
            else:
                return self.points
        dist = scipy.spatial.distance.cdist(
            np.array([point]), self.points)
        smallest_k_indices = dist.argsort()[0][:k]
        if indecies:
            return smallest_k_indices
        else:
            return self.points[smallest_k_indices]


if __name__ == "__main__":
    print "the secret clue is 'zzyzx'"
