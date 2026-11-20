"""
Plotting with polars is such a common use case in data science that we want to
make sure it works nicely with uniplot. Thus these tests.
"""

import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np  # type: ignore
import polars as pl
import pytest

from uniplot import plot, plot_to_string
from uniplot.multi_series import MultiSeries


def test_normal_plotting():
    data = pl.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )
    plot(xs=data["speed"], ys=data["vertical_rms"], x_unit=" km/h", y_unit=" g")


def test_logarithmic_plotting():
    data = pl.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, -55.3, np.nan],
        }
    )
    plot(xs=data["speed"], ys=data["vertical_rms"])


def test_that_polars_series_is_interpreted_as_single_dim_array():
    from uniplot.multi_series import MultiSeries

    data = pl.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )

    series = MultiSeries(xs=data["speed"], ys=data["vertical_rms"])
    assert not series.is_multi_dimensional


def test_grouped_plotting():
    data = pl.DataFrame(
        data={
            "asset": ["asset1", "asset1", "asset2", "asset3"],
            "speed": [20.0, 50.0, 75.6, 12.6],
            "vertical_rms": [12.4, 23.5, 55.3, 20.5],
        }
    )
    # TODO Should find a better way than with the `maintain_order` option
    grouped_data = data.group_by(["asset"], maintain_order=True)
    plot(
        xs=[group["speed"] for (_, group) in grouped_data],
        ys=[group["vertical_rms"] for (_, group) in grouped_data],
        x_unit=" km/h",
        y_unit=" g",
        lines=True,
    )


@pytest.mark.parametrize("axis", ["x", "y"])
def test_timezone_aware_datetime_labels(axis):
    start = datetime(2026, 1, 15, 9, tzinfo=ZoneInfo("Asia/Tokyo"))
    values = [start + timedelta(hours=i) for i in range(10)]
    data = pl.Series(values)
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
