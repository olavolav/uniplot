import numpy as np
import time

from uniplot import plot


def test_plotting_one_million_points():
    nr_samples = 1_000_000
    acceptable_time_in_seconds = 0.3

    ys = np.random.normal(0, 1, nr_samples)

    start_time = time.time()
    plot(ys)
    assert time.time() - start_time < acceptable_time_in_seconds
