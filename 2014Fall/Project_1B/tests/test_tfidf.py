from collections import Counter
import tfidf
import math
from nose.tools import eq_


def test_max_word_occurance():
    doc = Counter('')
    eq_(tfidf.max_word_occurance(doc), 0)

    doc1 = Counter('abbcccdddd')
    eq_(tfidf.max_word_occurance(doc1), 4)

    doc2 = Counter('abbcccddd')

    eq_(tfidf.max_word_occurance([doc1, doc2]), 4)


def test_tf():
    doc = Counter('abbcccdddd')
    eq_(tfidf.tf('', doc), 0.0)
    eq_(tfidf.tf('a', doc), 0.25)
    eq_(tfidf.tf('b', doc), 0.5)
    eq_(tfidf.tf('d', doc), 1.0)


def test_idf():
    doc_set = {i: Counter('a') for i in range(4)}
    doc_set.update({i: Counter('b') for i in range(4, 6)})

    eq_(tfidf.idf('a', doc_set), math.log(6 / 4.0))
    eq_(tfidf.idf('b', doc_set), math.log(6 / 2.0))
