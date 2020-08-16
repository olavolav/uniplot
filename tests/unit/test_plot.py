import math
import time
import numpy as np  # type: ignore

from uniplot.uniplot import plot


def test_plotting():
    xs = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs)

    # Here we are just testing that no error is thrown
    assert True


def test_performance():
    xs = [math.sin(i / 20) + i / 300 for i in range(1_000_000)]

    start_time = time.time()
    plot(xs)
    duration_in_seconds = time.time() - start_time

    assert duration_in_seconds < 0.3


if __name__ == "__main__":
    test_plotting()
