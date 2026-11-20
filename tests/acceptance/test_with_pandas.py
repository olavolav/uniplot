"""
Plotting with pandas is such a common use case in data science that we want to
make sure it works nicely with uniplot. Thus these tests.
"""

import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd  # type: ignore
import pytest

from uniplot import plot, plot_to_string
from uniplot.multi_series import MultiSeries


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


@pytest.mark.parametrize("axis", ["x", "y"])
@pytest.mark.parametrize("container", ["index", "series"])
def test_timezone_aware_datetime_labels(axis, container):
    values = pd.date_range("2026-01-15 09:00", periods=10, freq="h", tz="Asia/Tokyo")
    data = values if container == "index" else values.to_series()
    kwargs = {"ys": range(10), "xs": range(10), f"{axis}s": data}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        series = MultiSeries(**kwargs)
        output = plot_to_string(**kwargs, width=60, height=12)
    assert str(getattr(series, f"{axis}_timezone")) == "Asia/Tokyo"
    np.testing.assert_array_equal(
        getattr(series, f"{axis}s")[0], np.arange(10) * 3600 + values[0].timestamp()
    )
    labels = (
        output.splitlines()[-1]
        if axis == "x"
        else " ".join(
            row.split("│")[-1] for row in output.splitlines() if row.startswith("│")
        )
    )
    assert "12:00" in labels
    assert "00:00" not in labels


def test_nat_does_not_count_as_a_naive_datetime():
    value = datetime(2026, 1, 15, 12, tzinfo=ZoneInfo("Europe/Berlin"))
    series = MultiSeries(xs=pd.Series([pd.NaT, value]), ys=[1, 2])
    assert str(series.x_timezone) == "Europe/Berlin"
    assert np.isnan(series.xs[0][0])
    assert series.xs[0][1] == value.timestamp()
