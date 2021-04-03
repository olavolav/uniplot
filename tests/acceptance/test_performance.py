import numpy as np  # type: ignore
import time

from uniplot import plot


def test_plotting_one_million_points():
    nr_samples = 1_000_000
    # TODO Much of that time is actually spent generating the nice axis labels, which need to be improved. The good news is that axis labeling is independent of the number of data points, so it should be relatively easy to fix.
    acceptable_time_in_seconds = 0.5

    ys = np.random.normal(0, 1, nr_samples)

    start_time = time.time()
    plot(ys)
    assert time.time() - start_time < acceptable_time_in_seconds
