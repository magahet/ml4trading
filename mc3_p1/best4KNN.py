#!/usr/bin/env python

import random


def add_noise(x):
    '''Adds random noise to prevent weird div by 0 errors.'''
    return x * random.normalvariate(1.0, 0.0005)


if __name__ == '__main__':
    x_list = range(1000)
    random.shuffle(x_list)
    for x in x_list:
        print '{},{},{}'.format(x, x, add_noise(x % 200))
