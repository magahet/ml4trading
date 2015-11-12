#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import sys


if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1], header=None, names=['x', 'y'])
    df.plot(kind='scatter', x='x', y='y')
    plt.show()
