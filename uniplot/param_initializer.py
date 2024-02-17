import numpy as np
from typing import Dict

from uniplot.multi_series import MultiSeries
from uniplot.options import Options
from uniplot.conversions import floatify

AUTO_WINDOW_ENLARGE_FACTOR = 0.001


def validate_and_transform_options(series: MultiSeries, kwargs: Dict = {}) -> Options:
    """
    This will check the keyword arguments passed to the `uniplot.plot`
    function, will transform them and will return them in form of an `Options`
    object.

    The idea is to cast arguments into the right format to be used by the rest
    of the library, and to be as tolerant as possible for ease of use of the
    library.

    As a result the somewhat hacky code below should at least be confined to
    this function, and not spread throughout uniplot.
    """
    # First, some cleanup, including converting datetimes to float
    for key in ["x_min", "x_max", "y_min", "y_max"]:
        if key in kwargs:
            kwargs[key] = floatify(kwargs[key])
    # TODO y gridlines
    if "x_gridlines" in kwargs:
        kwargs["x_gridlines"] = [floatify(x) for x in kwargs["x_gridlines"]]

    if kwargs.get("x_as_log"):
        series.set_x_axis_to_log10()
        if not kwargs.get("x_gridlines"):
            kwargs["x_gridlines"] = []
        else:
            kwargs["x_gridlines"] = list(np.log10(np.array(kwargs["x_gridlines"])))
        if kwargs.get("x_min"):
            kwargs["x_min"] = np.log10(kwargs["x_min"])
        if kwargs.get("x_max"):
            kwargs["x_max"] = np.log10(kwargs["x_max"])
    if kwargs.get("y_as_log"):
        series.set_y_axis_to_log10()
        if not kwargs.get("y_gridlines"):
            kwargs["y_gridlines"] = []
        else:
            kwargs["y_gridlines"] = list(np.log10(np.array(kwargs["y_gridlines"])))
        if kwargs.get("y_min"):
            kwargs["y_min"] = np.log10(kwargs["y_min"])
        if kwargs.get("y_max"):
            kwargs["y_max"] = np.log10(kwargs["y_max"])

    # Set x bounds to show all points by default
    x_enlarge_delta = AUTO_WINDOW_ENLARGE_FACTOR * (
        floatify(series.x_max()) - floatify(series.x_min())
    )
    kwargs["x_min"] = floatify(
        kwargs.get("x_min", floatify(series.x_min()) - x_enlarge_delta)
    )
    kwargs["x_max"] = floatify(
        kwargs.get("x_max", floatify(series.x_max()) + x_enlarge_delta)
    )

    # Fallback for only a single data point, or multiple with single x coordinate
    if kwargs["x_min"] == kwargs["x_max"]:
        kwargs["x_min"] = kwargs["x_min"] - 1
        kwargs["x_max"] = kwargs["x_max"] + 1

    # Set y bounds to show all points by default
    y_enlarge_delta = AUTO_WINDOW_ENLARGE_FACTOR * (series.y_max() - series.y_min())
    kwargs["y_min"] = kwargs.get("y_min", series.y_min() - y_enlarge_delta)
    kwargs["y_max"] = kwargs.get("y_max", series.y_max() + y_enlarge_delta)

    # Fallback for only a single data point, or multiple with single y coordinate
    if float(kwargs["y_min"]) == float(kwargs["y_max"]):
        kwargs["y_min"] = kwargs["y_min"] - 1
        kwargs["y_max"] = kwargs["y_max"] + 1

    # Make sure the length of the labels is not exceeding the number of series
    if kwargs.get("legend_labels") is not None:
        kwargs["legend_labels"] = list(kwargs["legend_labels"])[0 : len(series)]

    # By default, enable color for multiple series, disable color for a single one
    kwargs["color"] = kwargs.get("color", len(series) > 1)

    # Set lines option for all series
    if not kwargs.get("lines"):
        # This will work for both unset lines option and `False`
        kwargs["lines"] = [False] * len(series)
    elif kwargs.get("lines") is True:
        # This is used to expand a single `True`
        kwargs["lines"] = [True] * len(series)
    elif len(kwargs.get("lines")) != len(series):  # type: ignore
        raise ValueError("Invalid 'lines' option.")

    return Options(**kwargs)
