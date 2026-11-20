"""
Plotting with NumPy is such a common use case in data science that we want to make sure it
works nicely with uniplot. Thus these tests.
"""

import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from uniplot import plot, plot_to_string
from uniplot.multi_series import MultiSeries


def test_normal_plotting():
    xs = np.arange(1, 100)
    ys = np.sin(xs) - 35.7
    plot(xs=xs, ys=ys, title="Simple NumPy test")


@pytest.mark.parametrize("axis", ["x", "y"])
def test_timezone_aware_datetime_labels(axis):
    start = datetime(2026, 1, 15, 9, tzinfo=ZoneInfo("Asia/Tokyo"))
    values = [start + timedelta(hours=i) for i in range(10)]
    data = np.array(values, dtype=object)
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
