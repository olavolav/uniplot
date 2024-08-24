import numpy as np
from numpy.typing import NDArray

from typing import List, Any


class MultiSeries:
    """
    A `MultiSeries` is an object that contains multiple series of numeric
    values in both x and y direction.

    If no `xs` parameter is supplied, then we generate x axis values as a
    serial index integer value.
    """

    def __init__(self, ys, xs=None) -> None:
        # Init types
        self.xs: List[NDArray] = []
        self.ys: List[NDArray] = []

        # First check if the input is multi-dim
        self.is_multi_dimensional: bool = _is_multi_dimensional(ys)

        self.x_is_time_series: bool = False
        self.y_is_time_series: bool = False

        # Initialize y series
        if self.is_multi_dimensional:
            self.y_is_time_series = all([_is_time_series(y) for y in ys])
            if self.y_is_time_series:
                self.ys = [_cast_as_numpy_time_series(ys_row) for ys_row in ys]
            else:
                self.ys = [_cast_as_numpy_floats(ys_row) for ys_row in ys]
        else:
            self.y_is_time_series = _is_time_series(ys)

            if self.y_is_time_series:
                self.ys = [_cast_as_numpy_time_series(ys)]
            else:
                self.ys = [_cast_as_numpy_floats(ys)]

        # Initialize x series
        if xs is None:
            # Initialize as a serial index
            self.xs = [np.arange(1, len(y) + 1, step=1, dtype=int) for y in self.ys]
        else:
            if self.is_multi_dimensional:
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

    def shape(self) -> List[int]:
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


def _is_time_series(series: Any) -> bool:
    """
    Check if the object is datetime-like. This might be a pandas DateTime, a
    list of datetimes, or a list of date(s).
    """
    np_array = np.array(series)
    if np.issubdtype(np_array.dtype, np.number):
        return False
    try:
        # Here we can omit the `[s]` to not cause unnecessary conversion work,
        # as the convertion to "datetime64[s]" is guaranteed to work later on,
        # if "datetime64" works.
        np_array.astype("datetime64")
        return True
    except Exception:
        return False


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


def _cast_as_numpy_time_series(series: Any) -> NDArray:
    """
    Converts to a numpy floating-point array, of unix epoch timestamps, with
    nano-second precision.

    We assume that at this point we have already checked that the conversion is
    possible.
    """
    # NOTE It is really important that throughout the library we use the
    # "datetime64[s]" NumPy format consistently. Using only `np.datetime`
    # or a different type like "datetime64[m]" means that the conversion to
    # floating point will depend on the input format, which will lead to
    # unexpected behavior.
    return np.array(series).astype("datetime64[s]").astype(float)


def _safe_max(array: NDArray) -> float:
    return array[~np.isnan(array)].max()


def _safe_maxs(series: List) -> float:
    return max([_safe_max(row) for row in series if len(row) > 0])


def _safe_mins(series: List) -> float:
    return min([_safe_min(row) for row in series if len(row) > 0])


def _safe_min(array: NDArray) -> float:
    return array[~np.isnan(array)].min()


def _safe_log10(x: NDArray) -> NDArray:
    x = x.astype(float)
    x[x <= 0.0] = np.nan
    return np.log10(x)
