import KNNLearner
from nose.tools import eq_


class TestBruteSpatial(object):

    def setup(self):
        data = [(0, 0), (1, 1), (2, 2), (3, 3)]
        self.db = KNNLearner.BruteSpatial(data)

    def test_query(self):
        eq_([
