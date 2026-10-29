"""
Plotting with pandas is such a common use case in data science that we want to
make sure it works nicely with uniplot. Thus these tests.
"""

import warnings

import numpy as np
import pandas as pd  # type: ignore

from uniplot import plot


def test_normal_plotting():
    data = pd.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )
    plot(xs=data["speed"], ys=data["vertical_rms"], x_unit=" km/h", y_unit=" g")


def test_logarithmic_plotting():
    data = pd.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, -55.3, np.nan],
        }
    )
    plot(xs=data["speed"], ys=data["vertical_rms"])


def test_that_pandas_series_is_interpreted_as_single_dim_array():
    from uniplot.multi_series import MultiSeries

    data = pd.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )

    series = MultiSeries(xs=data["speed"], ys=data["vertical_rms"])
    assert not series.is_multi_dimensional


def test_grouped_plotting():
    data = pd.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )
    grouped_data = data.groupby("asset")
    plot(
        xs=[group["speed"] for (_, group) in grouped_data],
        ys=[group["vertical_rms"] for (_, group) in grouped_data],
        x_unit=" km/h",
        y_unit=" g",
        lines=True,
    )


def test_plotting_time_series_from_pandas_index():
    dti = pd.date_range("2024-01-01", periods=4, freq="h")
    plot(xs=dti, ys=[1, 2, 3, 1])


def test_plotting_time_series_from_pandas_series():
    N = 150
    dti = pd.date_range("2024-01-01", periods=N, freq="MS")

    data = pd.DataFrame(np.random.randn(N, 1), columns=["value"], index=dti)
    data["date_as_series"] = data.index.to_series()

    plot(xs=data.date_as_series, ys=data.value, lines=True)


def test_plotting_timezone_aware_time_series_from_pandas():
    xs = pd.date_range("2026-10-28 00:00", periods=10, freq="h", tz="Asia/Tokyo")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        plot(xs=xs, ys=range(10))
        plot(xs=xs.to_series(), ys=range(10))
