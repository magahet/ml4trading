import mc3_p1.KNNLearner
import numpy as np


class TestBruteSpatial(object):

    def setup(self):
        data = np.array([(0, 0), (1, 1), (2, 2), (3, 3)])
        self.db = mc3_p1.KNNLearner.BruteSpatial(data)

    def test_query(self):

        # exact, one point
        point = np.array([0, 0])
        expected = np.array([[0, 0]])
        actual = self.db.search(point)
        np.testing.assert_array_equal(actual, expected)

        # exact, two points
        point = np.array([0, 0])
        expected = np.array([[0, 0], [1, 1]])
        actual = self.db.search(point, k=2)
        np.testing.assert_array_equal(actual, expected)

        # not exact, single point
        point = np.array([1, 0])
        expected = np.array([[0, 0]])
        actual = self.db.search(point)
        np.testing.assert_array_equal(actual, expected)

        # not exact, two points
        point = np.array([1, 0])
        expected = np.array([[0, 0], [1, 1]])
        actual = self.db.search(point, k=2)
        np.testing.assert_array_equal(actual, expected)
