#!/usr/bin/env python

import random


def add_noise(x):
    return x * random.normalvariate(1.0, 0.00005)


if __name__ == '__main__':
    data = []
    for x in xrange(1000):
        data.append('{},{}'.format(x, add_noise(1000 * x)))
    random.shuffle(data)
    for sample in data:
        print sample
