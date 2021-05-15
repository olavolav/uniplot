import numpy as np  # type: ignore
import math

from uniplot import plot, plot_to_string


def test_normal_plotting():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Sine wave")


def test_normal_plotting_to_string():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot_to_string(xs=x, ys=x, title="Sine wave")


def test_normal_plotting_with_x_series():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Diagonal")


def test_multi_series_plotting():
    ys = [
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) for i in range(1000)],
        # Make sure we also support plotting series of different length
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) - 1 for i in range(800)],
    ]
    plot(ys, title="Double sine wave", color=True)


def test_massively_multi_series_plotting():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    xt = np.array([x]).T
    plot(xt, title="Many colored dots", color=True)


def test_just_single_point_plotting():
    """
    Testing this because this has caused problems since for a single point min == max
    """
    x = [2.34]
    plot(x)


def test_random_line_plotting():
    xs = np.random.normal(size=100)
    ys = np.random.normal(size=100)
    plot(xs=xs, ys=ys, lines=True)
