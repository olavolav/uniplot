import numpy as np
from typing import Dict

from uniplot.multi_series import MultiSeries
from uniplot.options import Options, CharacterSet
from uniplot.conversions import floatify
from uniplot.colors import Color
from uniplot.color_themes import COLOR_THEMES

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
    elif series.x_is_time_series:
        # Default to no x gridlines
        kwargs["x_gridlines"] = []

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

    # Colors of gridlines
    kwargs["x_gridlines_color"] = kwargs.get("x_gridlines_color", False)
    kwargs["x_gridlines_color"] = _init_color_from_arg(kwargs["x_gridlines_color"])
    kwargs["y_gridlines_color"] = kwargs.get("y_gridlines_color", False)
    kwargs["y_gridlines_color"] = _init_color_from_arg(kwargs["y_gridlines_color"])

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

    # Fallback for only a single data point, or multiple with single x
    # coordinate
    if kwargs["x_min"] == kwargs["x_max"]:
        kwargs["x_min"] = kwargs["x_min"] - 1
        kwargs["x_max"] = kwargs["x_max"] + 1

    # Set y bounds to show all points by default
    y_enlarge_delta = AUTO_WINDOW_ENLARGE_FACTOR * (series.y_max() - series.y_min())
    kwargs["y_min"] = kwargs.get("y_min", series.y_min() - y_enlarge_delta)
    kwargs["y_max"] = kwargs.get("y_max", series.y_max() + y_enlarge_delta)

    # Fallback for only a single data point, or multiple with single y
    # coordinate
    if float(kwargs["y_min"]) == float(kwargs["y_max"]):
        kwargs["y_min"] = kwargs["y_min"] - 1
        kwargs["y_max"] = kwargs["y_max"] + 1

    # Explicit conversion to string of text options
    for key in ["title", "x_unit", "y_unit"]:
        if key in kwargs:
            kwargs[key] = str(kwargs[key])
    if kwargs.get("legend_labels") is not None:
        kwargs["legend_labels"] = [
            # Make sure the length of the labels is not exceeding the number of
            # series
            str(s)
            for s in list(kwargs["legend_labels"])[0 : len(series)]
        ]

    # By default, enable color for multiple series, disable color for a single
    # one
    kwargs["color"] = kwargs.get("color", len(series) > 1)
    kwargs["color"] = _init_color_from_arg(kwargs["color"])

    # TODO Remove this after July 2025, to give folks 3 months to adapt.
    if "force_ascii" in kwargs:
        print(
            "Warning: the force_ascii option is deprecated. Please use the character_set option instead."
        )
        del kwargs["force_ascii"]

    if "character_set" in kwargs:
        cs_string = str(kwargs["character_set"]).strip().lower()
        if cs_string == "ascii":
            kwargs["character_set"] = CharacterSet.ASCII
        elif cs_string == "block":
            kwargs["character_set"] = CharacterSet.BLOCK
        elif cs_string == "braille":
            kwargs["character_set"] = CharacterSet.BRAILLE
        else:
            raise ValueError("Invalid 'character_set' option.")

    if "force_ascii_characters" in kwargs:
        # In ASCII mode, simply slice to only use the first character
        kwargs["force_ascii_characters"] = [
            (str(x) + "#")[0] for x in kwargs["force_ascii_characters"]
        ]

    # Set lines option for all series
    if not kwargs.get("lines"):
        # This will work for both unset lines option and `False`
        kwargs["lines"] = [False] * len(series)
    elif kwargs.get("lines") is True:
        # This is used to expand a single `True`
        kwargs["lines"] = [True] * len(series)
    elif len(kwargs.get("lines")) != len(series):  # type: ignore
        raise ValueError("Invalid 'lines' option.")

    options = Options(**kwargs)

    # Check for invalid or unsupported combinations
    if (series.x_is_time_series and options.x_as_log) or (
        series.y_is_time_series and options.y_as_log
    ):
        raise ValueError(
            "We currently do not support using timestamps on a log scale. We suggest to convert the timestamps to numbers first."
        )

    return options


###########
# private #
###########


def _init_color_from_arg(color_arg):
    # If it is a string, it refers to a color theme
    if isinstance(color_arg, str):
        theme_str = color_arg.strip().lower()
        if theme_str not in COLOR_THEMES:
            raise ValueError(
                f"Color theme '{color_arg}' not found. If you intended to specify a single color, pass a list with that entry."
            )
        return COLOR_THEMES[theme_str]

    # Convert list of color specifications to Color objects
    if isinstance(color_arg, list):
        return [Color.from_param(cs) for cs in color_arg]

    # Default when passing bool value
    if color_arg is True:
        return COLOR_THEMES["default"]

    # Otherwise assume no color
    return False
