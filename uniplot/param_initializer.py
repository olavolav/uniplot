import datetime
from numbers import Real

import numpy as np

from uniplot.axis_labels.label_set import VALID_UNIT_SCALINGS
from uniplot.color_themes import COLOR_THEMES
from uniplot.colors import Color
from uniplot.conversions import floatify
from uniplot.datetimes import is_missing, pad_datetime_bound, validate_datetime_option
from uniplot.legend_placements import LegendPlacement
from uniplot.multi_series import MultiSeries
from uniplot.options import CharacterSet, Options

AUTO_WINDOW_ENLARGE_FACTOR = 0.001


def validate_and_transform_options(
    series: MultiSeries,
    kwargs: dict | None = None,
    bounds_already_in_plot_space: frozenset = frozenset(),
) -> Options:
    """
    This will check the keyword arguments passed to the `uniplot.plot`
    function, will transform them and will return them in form of an `Options`
    object.

    The idea is to cast arguments into the right format to be used by the rest
    of the library, and to be as tolerant as possible for ease of use of the
    library.

    As a result the somewhat hacky code below should at least be confined to
    this function, and not spread throughout uniplot.

    `bounds_already_in_plot_space` is for internal use by `plot_gen`: it lists
    the bound keys (a subset of `x_min`/`x_max`/`y_min`/`y_max`) whose values
    are already in plot space, i.e. pinned bounds that were re-injected from a
    previous render. For those we must not apply the `log10` transform again.
    """
    if kwargs is None:
        kwargs = {}

    # TODO Remove rounded_corners no earlier than 2027-05-14 (six months).
    if "rounded_corners" in kwargs:
        print(
            "Warning: the rounded_corners option is deprecated and will be removed "
            'no earlier than May 14, 2027. Please use border="rounded" or '
            'border="box" instead.'
        )

    if kwargs.get("fill") is not None:
        # Invalid samples break filled paths and must not poison automatic bounds.
        series.xs = [np.where(np.isfinite(x), x, np.nan) for x in series.xs]
        series.ys = [np.where(np.isfinite(y), y, np.nan) for y in series.ys]

    # First, some cleanup, including converting datetimes to float
    for key in ["x_min", "x_max", "y_min", "y_max"]:
        if key in kwargs:
            if getattr(series, f"{key[0]}_is_time_series"):
                validate_datetime_option(
                    kwargs[key], getattr(series, f"{key[0]}_timezone"), key
                )
            kwargs[key] = floatify(kwargs[key])
    for axis in ("x", "y"):
        key = f"{axis}_gridlines"
        if key in kwargs:
            if getattr(series, f"{axis}_is_time_series"):
                for value in kwargs[key]:
                    validate_datetime_option(
                        value, getattr(series, f"{axis}_timezone"), key
                    )
            kwargs[key] = [floatify(value) for value in kwargs[key]]
        elif getattr(series, f"{axis}_is_time_series"):
            kwargs[key] = []

    if kwargs.get("x_as_log"):
        series.set_x_axis_to_log10()
        if not kwargs.get("x_gridlines"):
            kwargs["x_gridlines"] = []
        else:
            kwargs["x_gridlines"] = list(np.log10(np.array(kwargs["x_gridlines"])))
        if kwargs.get("x_min") and "x_min" not in bounds_already_in_plot_space:
            kwargs["x_min"] = np.log10(kwargs["x_min"])
        if kwargs.get("x_max") and "x_max" not in bounds_already_in_plot_space:
            kwargs["x_max"] = np.log10(kwargs["x_max"])
    if kwargs.get("y_as_log"):
        series.set_y_axis_to_log10()
        if not kwargs.get("y_gridlines"):
            kwargs["y_gridlines"] = []
        else:
            kwargs["y_gridlines"] = list(np.log10(np.array(kwargs["y_gridlines"])))
        if kwargs.get("y_min") and "y_min" not in bounds_already_in_plot_space:
            kwargs["y_min"] = np.log10(kwargs["y_min"])
        if kwargs.get("y_max") and "y_max" not in bounds_already_in_plot_space:
            kwargs["y_max"] = np.log10(kwargs["y_max"])

    kwargs["fill"] = _normalize_fill(
        kwargs.get("fill"), series, kwargs.get("y_as_log", False)
    )

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
        kwargs.get(
            "x_min",
            pad_datetime_bound(
                series.x_min(), series.x_min() - x_enlarge_delta, series.x_timezone
            ),
        )
    )
    kwargs["x_max"] = floatify(
        kwargs.get(
            "x_max",
            pad_datetime_bound(
                series.x_max(), series.x_max() + x_enlarge_delta, series.x_timezone
            ),
        )
    )

    # Fallback for only a single data point, or multiple with single x
    # coordinate
    if kwargs["x_min"] == kwargs["x_max"]:
        kwargs["x_min"] = kwargs["x_min"] - 1
        kwargs["x_max"] = kwargs["x_max"] + 1

    # Set y bounds to show all points by default
    y_min, y_max = series.y_min(), series.y_max()
    for xs, ys, baseline in zip(series.xs, series.ys, kwargs["fill"]):
        if baseline is None or baseline == "bottom":
            continue
        finite = np.isfinite(xs) & np.isfinite(ys)
        has_area = (
            finite[:-1]
            & finite[1:]
            & (xs[:-1] != xs[1:])
            & ((ys[:-1] != baseline) | (ys[1:] != baseline))
        )
        if np.any(has_area):
            y_min, y_max = min(y_min, baseline), max(y_max, baseline)
    y_enlarge_delta = AUTO_WINDOW_ENLARGE_FACTOR * (y_max - y_min)
    kwargs["y_min"] = kwargs.get(
        "y_min", pad_datetime_bound(y_min, y_min - y_enlarge_delta, series.y_timezone)
    )
    kwargs["y_max"] = kwargs.get(
        "y_max", pad_datetime_bound(y_max, y_max + y_enlarge_delta, series.y_timezone)
    )

    # Fallback for only a single data point, or multiple with single y
    # coordinate
    if float(kwargs["y_min"]) == float(kwargs["y_max"]):
        kwargs["y_min"] = kwargs["y_min"] - 1
        kwargs["y_max"] = kwargs["y_max"] + 1

    # Explicit conversion to string of text options
    for key in ["title", "x_unit", "y_unit"]:
        if key in kwargs:
            kwargs[key] = str(kwargs[key])

    # Normalize and validate unit scaling options
    for key in ["x_unit_scaling", "y_unit_scaling"]:
        if key in kwargs:
            value = str(kwargs[key]).strip().lower()
            if value not in VALID_UNIT_SCALINGS:
                valid = ", ".join(repr(v) for v in sorted(VALID_UNIT_SCALINGS))
                raise ValueError(
                    f"Invalid '{key}' option: {kwargs[key]!r}. "
                    f"Valid values are: {valid}."
                )
            kwargs[key] = value
    if kwargs.get("legend_labels") is not None:
        kwargs["legend_labels"] = [
            # Make sure the length of the labels is not exceeding the number of
            # series
            str(s)
            for s in list(kwargs["legend_labels"])[0 : len(series)]
        ]

    if "legend_placement" in kwargs:
        kwargs["legend_placement"] = LegendPlacement.from_string(
            kwargs["legend_placement"]
        )

    # By default, enable color for multiple series, disable color for a single
    # one
    kwargs["color"] = kwargs.get("color", len(series) > 1)
    kwargs["color"] = _init_color_from_arg(kwargs["color"])

    if "character_set" in kwargs:
        kwargs["character_set"] = CharacterSet.from_string(kwargs["character_set"])

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
            try:
                c = Color.from_terminal(theme_str)
                print(
                    f'Warning: Please use a list such as ["{color_arg}"] to specify a single named color.'
                )
                return [c]
            except ValueError:
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


def _normalize_fill(value, series: MultiSeries, log: bool) -> list:
    values = value if isinstance(value, list) else [value] * len(series)
    if len(values) != len(series):
        raise ValueError("fill must have one entry per series.")
    result: list[float | str | None] = []
    for baseline in values:
        if baseline is None or (isinstance(baseline, str) and baseline == "bottom"):
            result.append(baseline)
            continue
        is_datetime = isinstance(baseline, (datetime.date, np.datetime64))
        if is_datetime:
            if not series.y_is_time_series or is_missing(baseline):
                raise ValueError(
                    "fill requires a valid datetime baseline on a datetime y axis."
                )
        elif isinstance(baseline, (bool, np.bool_)) or not isinstance(baseline, Real):
            raise ValueError(
                'fill must be None, "bottom", a finite baseline, or a per-series list.'
            )
        if is_datetime:
            validate_datetime_option(baseline, series.y_timezone, "fill")
        baseline = floatify(baseline)
        if not np.isfinite(baseline) or (log and baseline <= 0):
            raise ValueError(
                "fill baseline must be finite and positive on a logarithmic y axis."
            )
        result.append(float(np.log10(baseline)) if log else baseline)
    return result
