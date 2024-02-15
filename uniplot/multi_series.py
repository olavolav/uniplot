import numpy as np
from numpy.typing import NDArray

from typing import List


class MultiSeries:
    """
    A `MultiSeries` is an object that contains multiple series of numeric values in both x and y direction.

    If no `xs` parameter is supplied, then we generate x axis values as a serial index integer value.
    """

    def __init__(self, ys, xs=None) -> None:
        # Init types
        self.xs: List[NDArray] = []
        self.ys: List[NDArray] = []

        # First check if the input is multi-dim
        self.is_multi_dimensional: bool = _is_multi_dimensional(ys)

        # Initialize y series
        if self.is_multi_dimensional:
            self.ys = [_cast_as_numpy_floats(ys_row) for ys_row in ys]
        else:
            self.ys = [_cast_as_numpy_floats(ys)]

        self.x_is_time_series: bool = False

        # Initialize x series
        if xs is None:
            self.xs = [np.arange(1, len(y) + 1, step=1, dtype=int) for y in self.ys]
        else:
            if self.is_multi_dimensional:
                # check if all x series are time series
                # TODO Do that for y as well
                self.x_is_time_series = all([_is_time_series(x) for x in xs])

                if self.x_is_time_series:
                    self.xs = [_cast_as_numpy_time_series(xs_row) for xs_row in xs]
                else:
                    self.xs = [_cast_as_numpy_floats(xs_row) for xs_row in xs]
            else:
                self.x_is_time_series = _is_time_series(xs)

                if self.x_is_time_series:
                    self.xs = [_cast_as_numpy_time_series(xs)]
                else:
                    self.xs = [_cast_as_numpy_floats(xs)]
        print(f"DEBUG: x_is_time_series = {self.x_is_time_series}")

    def __len__(self) -> int:
        """Return the number of time series."""
        return len(self.ys)

    def shape(self) -> List[int]:
        """Return a list with the length of the time series."""
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
        """Apply log10 to all y series."""
        self.ys = [_safe_log10(y) for y in self.ys]

    def y_max(self) -> float:
        return max([_safe_max(ys_row) for ys_row in self.ys])

    def y_min(self) -> float:
        return min([_safe_min(ys_row) for ys_row in self.ys])

    def x_max(self) -> float:
        return max([_safe_max(xs_row) for xs_row in self.xs])

    def x_min(self) -> float:
        return min([_safe_min(xs_row) for xs_row in self.xs])


###########
# private #
###########


def _is_multi_dimensional(series) -> bool:
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


def _is_time_series(series) -> bool:
    """
    Check if the object is datetime-like. This might be a pandas DateTime, a
    list of datetimes, or a list of date(s).
    """
    try:
        np.array(series, dtype="datetime64[ns]")
        return True
    # if series.dtype == "datetime64[ns]":
    #     return True
    # elif isinstance(series, list):
    #     if all(isinstance(x, datetime.date) for x in series):
    #         return True
    #     elif all(isinstance(x, datetime.datetime) for x in series):
    #         return True

    except:
        return False


def _cast_as_numpy_floats(array) -> NDArray:
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


def _cast_as_numpy_time_series(series) -> NDArray:
    """
    Converts to a numpy floating-point array, of unix epoch timestamps,
    with nano-second precision.
    """
    # series = series.astype(np.int64) // 10**9

    # finally, convert to numpy array
    # return series  # .values
    return np.array(series, dtype="datetime64[ns]")


def _safe_max(array) -> float:
    return array[~np.isnan(array)].max()


def _safe_min(array) -> float:
    return array[~np.isnan(array)].min()


def _safe_log10(x: NDArray) -> NDArray:
    x = x.astype(float)
    x[x <= 0.0] = np.nan
    return np.log10(x)
