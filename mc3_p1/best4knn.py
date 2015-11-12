#!/usr/bin/env python

import random


def add_noise(x):
    return x * random.normalvariate(1.0, 0.005)


if __name__ == '__main__':
    x_list = range(1000)
    random.shuffle(x_list)
    for x in x_list:
        print '{},{}'.format(x, add_noise(x % 200))
