import numpy as np  # type: ignore

from uniplot.multi_series import MultiSeries


def test_length_and_shape_when_only_passing_single_ys_as_list():
    ys = [1, 2, 3]
    series = MultiSeries(ys=ys)

    assert len(series) == 1
    assert series.shape() == [3]


def test_length_and_shape_when_passing_multiple_lists():
    ys = [[1, 222, 3, -3.14, 0], [1, 222, 3, -3.14, 0, 4, 4, 4], [1]]
    xs = [[1000, 222, 3, -314, 0], [0, 2222, 3, -3.14, 0, 4, 4, 4], [1]]
    series = MultiSeries(xs=xs, ys=ys)

    assert len(series) == 3
    assert series.shape() == [5, 8, 1]


def test_min_and_max():
    ys = [[1, 222, 3, -3.14, 0], [1, 222, 3, -3.14, 0]]
    xs = [[1000, 222, 3, -314, 0], [0, 2222, 3, -3.14, 0]]
    series = MultiSeries(xs=xs, ys=ys)

    assert series.x_min() == -314
    assert series.x_max() == 2222
    assert series.y_min() == -3.14
    assert series.y_max() == 222


def test_occasional_nans_should_be_tolerated():
    xs = [[3.0, 2.5, np.nan, 1.0, 1.5]]
    ys = [[13.0, 22.5, 22.9, np.nan, 41.0]]
    series = MultiSeries(xs=xs, ys=ys)

    assert series.shape() == [5]
