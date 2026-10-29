import numpy as np

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


def test_setting_x_axis_to_logarithmic():
    xs = [1.0, 10.0, np.nan, 100.0, -1000.0, 0.0]
    ys = [13.0, 22.5, 22.9, np.nan, 41.0, np.nan]
    series = MultiSeries(xs=xs, ys=ys)
    series.set_x_axis_to_log10()

    # X axis should now be logarithmic
    desired = np.array([0.0, 1.0, np.nan, 2.0, np.nan, np.nan])
    np.testing.assert_array_equal(series.xs, [desired])
    # Y axis should not be changed
    np.testing.assert_array_equal(series.ys, [ys])


def test_setting_y_axis_to_logarithmic():
    xs = [13.0, 22.5, 22.9, np.nan, 41.0, np.nan]
    ys = [1.0, 10.0, np.nan, 100.0, -1000.0, 0.0]
    series = MultiSeries(xs=xs, ys=ys)
    series.set_y_axis_to_log10()

    # X axis should not be changed
    np.testing.assert_array_equal(series.xs, [xs])
    # X axis should now be logarithmic
    desired = np.array([0.0, 1.0, np.nan, 2.0, np.nan, np.nan])
    np.testing.assert_array_equal(series.ys, [desired])


def test_normal_series_without_xs_should_not_be_time_series():
    ys = [1, 2, 3]
    series = MultiSeries(ys=ys)

    assert not series.x_is_time_series


def test_normal_series_with_xs_should_not_be_time_series():
    xs = [-1, 2, 30]
    ys = [1, 2, 3]
    series = MultiSeries(xs=xs, ys=ys)

    assert not series.x_is_time_series


def test_time_series_should_be_detected_as_such():
    dates = np.arange("2002-10-27T04:30", 4 * 60, 60, dtype="M8[m]")
    ys = [1, 2, 3, 4]
    series = MultiSeries(xs=dates, ys=ys)

    assert series.x_is_time_series


def test_timezone_aware_pandas_xs_keep_their_timezone():
    import pandas as pd  # type: ignore

    xs = pd.date_range("2024-08-01 09:00", periods=3, freq="h", tz="Asia/Tokyo")
    series = MultiSeries(ys=[1, 2, 3], xs=xs)

    assert series.x_is_time_series
    assert str(series.x_timezone) == "Asia/Tokyo"
    assert series.xs[0][0] == np.datetime64("2024-08-01T00:00").astype(
        "datetime64[s]"
    ).astype(float)
