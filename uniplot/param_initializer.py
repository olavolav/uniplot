import numpy as np  # type: ignore
from typing import Dict, Tuple, List, Optional, Any

from uniplot.multi_series import MultiSeries
from uniplot.options import Options


def validate_and_transform_options(series: MultiSeries, kwargs: Dict = {}) -> Options:
    """
    This will check the keyword arguments passed to the `uniplot.plot` function, will transform them and will return them in form of an `Options` object.
    """
    # Set bounds to show all points by default
    kwargs["x_min"] = kwargs.get("x_min") or series.x_min()
    kwargs["x_max"] = kwargs.get("x_max") or (
        series.x_max() + 1e-4 * (series.x_max() - series.x_min())
    )
    if float(kwargs["x_min"]) == float(kwargs["x_max"]):
        kwargs["x_min"] = kwargs["x_min"] - 1
        kwargs["x_max"] = kwargs["x_max"] + 1
    kwargs["y_min"] = kwargs.get("y_min") or series.y_min()
    kwargs["y_max"] = kwargs.get("y_max") or (
        series.y_max() + 1e-4 * (series.y_max() - series.y_min())
    )
    if float(kwargs["y_min"]) == float(kwargs["y_max"]):
        kwargs["y_min"] = kwargs["y_min"] - 1
        kwargs["y_max"] = kwargs["y_max"] + 1

    # Make sure the length of the labels is not exceeding the number of series
    if kwargs.get("legend_labels") is not None:
        kwargs["legend_labels"] = list(kwargs["legend_labels"])[0 : len(series)]

    if "color" not in kwargs:
        kwargs["color"] = len(series) > 1

    return Options(**kwargs)
