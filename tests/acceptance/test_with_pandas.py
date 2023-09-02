"""
Plotting with pandas is such a common use case in data science that we want to make sure
it works nicely with uniplot. Thus these tests.
"""

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
        lines=True
    )
