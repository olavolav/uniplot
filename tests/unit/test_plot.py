import math
import time
import numpy as np  # type: ignore

from uniplot.uniplot import plot


def test_plotting():
    xs = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs)

    # Here we are just testing that no error is thrown
    assert True


if __name__ == "__main__":
    test_plotting()
