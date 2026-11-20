from datetime import tzinfo
from typing import Any

import numpy as np
from numpy.typing import NDArray

from uniplot.datetimes import DatetimeSeries, axis_timezone, normalize_datetime_series


class MultiSeries:
    """
    A `MultiSeries` is an object that contains multiple series of numeric
    values in both x and y direction.

    If no `xs` parameter is supplied, then we generate x axis values as a
    serial index integer value.
    """

    def __init__(self, ys, xs=None) -> None:
        # Init types
        self.xs: list[NDArray] = []
        self.ys: list[NDArray] = []

        # First check if the input is multi-dim
        self.is_multi_dimensional: bool = _is_multi_dimensional(ys)

        y_rows = list(ys) if self.is_multi_dimensional else [ys]
        self.ys, self.y_is_time_series, self.y_timezone = _normalize_axis(y_rows, "y")
        self.x_timezone: tzinfo | None = None
        self.x_is_time_series = False
        if xs is None:
            self.xs = [np.arange(1, len(y) + 1, dtype=int) for y in self.ys]
        else:
            x_rows = list(xs) if self.is_multi_dimensional else [xs]
            self.xs, self.x_is_time_series, self.x_timezone = _normalize_axis(
                x_rows, "x"
            )

        # In the end, the dimensions of xs and ys need to match
        assert len(self.xs) == len(self.ys)
        assert [len(xs_row) for xs_row in self.xs] == [
            len(ys_row) for ys_row in self.ys
        ]

    def __len__(self) -> int:
        """
        Return the number of time series.
        """
        return len(self.ys)

    def __str__(self) -> str:
        return f"MultiSeries(xs={self.xs}, ys={self.ys}, is_multi_dimensional={self.is_multi_dimensional}, x_is_time_series={self.x_is_time_series}, y_is_time_series={self.y_is_time_series})"

    def shape(self) -> list[int]:
        """
        Return a list with the length of the time series.
        """
        return [len(ys_row) for ys_row in self.ys]

    def set_x_axis_to_log10(self) -> None:
        """
        Apply log10 to all x series.

        Raises a `ValueError` if any the x-axis is a time series.
        """
        if self.x_is_time_series:
            raise ValueError("Cannot format a time series as logarithmic.")

        self.xs = [_safe_log10(x) for x in self.xs]

    def set_y_axis_to_log10(self) -> None:
        """
        Apply log10 to all y series.

        Raises a `ValueError` if any the x-axis is a time series.
        """
        if self.y_is_time_series:
            raise ValueError("Cannot format a time series as logarithmic.")

        self.ys = [_safe_log10(y) for y in self.ys]

    def y_max(self) -> float:
        return _safe_maxs(self.ys)

    def y_min(self) -> float:
        return _safe_mins(self.ys)

    def x_max(self) -> float:
        return _safe_maxs(self.xs)

    def x_min(self) -> float:
        return _safe_mins(self.xs)


###########
# private #
###########


def _is_multi_dimensional(series: Any) -> bool:
    """
    Check if the object is multi-dimensional.

    Ref.: https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    """
    try:
        [iter(x) for x in series]
    except TypeError:
        return False
    else:
        return True


def _normalize_axis(rows: list, axis: str) -> tuple[list[NDArray], bool, tzinfo | None]:
    dates = [normalize_datetime_series(row) for row in rows]
    # Empty and all-missing numeric rows must not erase another row's timezone.
    has_dates = any(row is not None for row in dates)
    if has_dates:
        for i, row in enumerate(dates):
            if row is None:
                values = _cast_as_numpy_floats(rows[i])
                if np.isnan(values).all():
                    dates[i] = DatetimeSeries(values, [])
        if all(row is not None for row in dates):
            valid_rows = [row for row in dates if row is not None]
            return (
                [row.values for row in valid_rows],
                True,
                axis_timezone(valid_rows, axis),
            )
    return [_cast_as_numpy_floats(row) for row in rows], False, None


def _cast_as_numpy_floats(array: Any) -> NDArray:
    """
    Attempts to make a numeric NumPy array from enumerable input.

    If simply casting into a NumPy array yields one of `numpy.inexact`
    floating-point type, it returns the array. Otherwise, it attempts to cast
    it as NumPy float.
    """
    numpy_array = np.array(array)
    if np.issubdtype(numpy_array.dtype, np.inexact):
        return numpy_array
    # If it not already intitializes as a numeric type, then all we can do is
    # attempt to cast to float (including NaNs)
    return numpy_array.astype(float)


def _safe_max(array: NDArray) -> float:
    values = array[~np.isnan(array)]
    return values.max() if len(values) else -np.inf


def _safe_maxs(series: list) -> float:
    result = max([_safe_max(row) for row in series if len(row) > 0])
    if result == -np.inf:
        raise ValueError("No valid data available to determine plot bounds.")
    return result


def _safe_mins(series: list) -> float:
    result = min([_safe_min(row) for row in series if len(row) > 0])
    if result == np.inf:
        raise ValueError("No valid data available to determine plot bounds.")
    return result


def _safe_min(array: NDArray) -> float:
    values = array[~np.isnan(array)]
    return values.min() if len(values) else np.inf


def _safe_log10(x: NDArray) -> NDArray:
    x = x.astype(float)
    x[x <= 0.0] = np.nan
    return np.log10(x)
