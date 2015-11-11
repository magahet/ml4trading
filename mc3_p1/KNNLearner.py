"""
A simple wrapper for linear regression.  (c) 2015 Tucker Balch
"""

import numpy as np
import scipy
import heapq


class LinRegLearner(object):

    def __init__(self):
        pass  # move along, these aren't the drones you're looking for

    def addEvidence(self, dataX, dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        # slap on 1s column so linear regression finds a constant term
        newdataX = np.ones([dataX.shape[0], dataX.shape[1] + 1])
        newdataX[:, 0:dataX.shape[1]] = dataX

        # build and save the model
        self.model_coefs, residuals, rank, s = np.linalg.lstsq(newdataX, dataY)

    def query(self, points):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        return (self.model_coefs[:-1] * points).sum(axis=1) + self.model_coefs[-1]


class BruteSpatial(object):
    '''Implements a naive spacial data structure.'''

    def __init__(self, points):
        self.points = points

    def search(self, query_point, k=1):
        '''Perform brute force knn search.'''
        neighbors = []
        for point in self.points:
            inv_dist = -scipy.spatial.distance.euclidean(query_point, point)
            if len(neighbors) < k:
                heapq.heappush(neighbors, (inv_dist, point))
            else:
                heapq.heappushpop(neighbors, (inv_dist, point))
        return [t[1] for t in neighbors]


if __name__ == "__main__":
    print "the secret clue is 'zzyzx'"
