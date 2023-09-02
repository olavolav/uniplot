import math
from random import random

from uniplot import plot, plot_to_string


def test_normal_plotting():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Sine wave")


def test_normal_plotting_to_string():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot_to_string(xs=x, ys=x, title="Sine wave")


def test_plotting_with_forced_ascii():
    x = [1, 3, -2]
    strs = plot_to_string(xs=x, ys=x, title="Sine wave in ASCII", force_ascii=True)
    assert "█" in "".join(strs)


def test_normal_plotting_with_x_series():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Diagonal")


def test_logarithmic_plotting():
    xs = range(1, 1000, 20)
    ys = [x**2 + 1e-6 for x in xs]
    plot(xs=xs, ys=ys, x_as_log=True, y_as_log=True)


def test_logarithmic_plotting_should_silently_ignore_negative_and_zero_values():
    ys = [-1.0, 0.0, 1.0, 20.09]
    plot(ys, y_as_log=True)


def test_multi_series_plotting():
    ys = [
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) for i in range(1000)],
        # Make sure we also support plotting series of different length
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) - 1 for i in range(800)],
    ]
    plot(ys, title="Double sine wave", color=True)


def test_massively_multi_series_plotting():
    many_single_dot_series = [[math.sin(i / 20) + i / 300] for i in range(600)]
    plot(many_single_dot_series, title="Many colored dots", color=True)


def test_just_single_point_plotting():
    """
    Testing this because this has caused problems since for a single point min == max
    """
    x = [2.34]
    plot(x)


def test_random_line_plotting():
    xs = [random() for _ in range(100)]
    ys = [random() for _ in range(100)]
    plot(xs=xs, ys=ys, lines=True)
