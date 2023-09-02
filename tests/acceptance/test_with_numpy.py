"""
Plotting with NumPy is such a common use case in data science that we want to make sure it
works nicely with uniplot. Thus these tests.
"""

import numpy as np

from uniplot import plot


def test_normal_plotting():
    xs = np.arange(1, 100)
    ys = np.sin(xs) - 35.7
    plot(xs=xs, ys=ys, title="Simple NumPy test")
