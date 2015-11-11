#!/usr/bin/env python

import random


def add_noise(x):
    return x * random.normalvariate(1.0, 0.005)


if __name__ == '__main__':
    for x in xrange(1000):
        print '{},{}'.format(x, add_noise(2 * x))
