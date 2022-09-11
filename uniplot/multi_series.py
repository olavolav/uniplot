import numpy as np  # type: ignore
from typing import List, Any


def _is_multi_dimensional(series) -> bool:
    try:
        # HACK
        series[0][0]
        return True
    except:
        return False


def _cast_as_numpy_floats(array) -> Any:
    """
    Attempts to make a numeric NumPy array from enumerable input. If simply casting into a NumPy array yields one of numeric type, it returns the array. Otherwise, it attempts to cast it as NumPy float.
    """
    numpy_array = np.array(array)
    if np.issubdtype(numpy_array.dtype, np.number):
        return numpy_array
    return numpy_array.astype(float)


class MultiSeries:
    def __init__(self, ys, xs=None):
        # Init types
        self.xs: List[Any] = []
        self.ys: List[Any] = []

        # First check if the input is multi-dim
        we_have_input_of_multiple_series = _is_multi_dimensional(ys)

        # Initialize y series
        if we_have_input_of_multiple_series:
            self.ys = [_cast_as_numpy_floats(ys_row) for ys_row in ys]
        else:
            self.ys = [_cast_as_numpy_floats(ys)]

        # Initialize x series
        if xs is None:
            self.xs = [
                np.arange(1, len(ys_row) + 1, step=1, dtype=int) for ys_row in self.ys
            ]
        else:
            if we_have_input_of_multiple_series:
                self.xs = [_cast_as_numpy_floats(xs_row) for xs_row in xs]
            else:
                self.xs = [_cast_as_numpy_floats(xs)]

        # Get rid of (ignore) NAN points. The goal here is to mimick the NAN-tolerance of NumPy or Apache Spark: Plotting should silently ignore NAN values.
        for i in range(len(self.ys)):
            invalid_indices = np.isnan(self.xs[i]) | np.isnan(self.ys[i])
            self.xs[i] = self.xs[i][~invalid_indices]
            self.ys[i] = self.ys[i][~invalid_indices]

            if len(self.xs[i]) == 0 or len(self.ys[i]) == 0:
                raise ValueError("Length of series must not be zero.")

    def __len__(self) -> int:
        """Return the number of time series."""
        return len(self.ys)

    def shape(self) -> List[int]:
        """Return a list with the length of the time series."""
        return [len(ys_row) for ys_row in self.ys]

    def y_max(self) -> float:
        return max([ys_row.max() for ys_row in self.ys])

    def y_min(self) -> float:
        return min([ys_row.min() for ys_row in self.ys])

    def x_max(self) -> float:
        return max([xs_row.max() for xs_row in self.xs])

    def x_min(self) -> float:
        return min([xs_row.min() for xs_row in self.xs])
