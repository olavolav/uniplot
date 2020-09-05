import numpy as np  # type: ignore
from typing import List, Optional


def _is_multi_dimensional(series) -> bool:
    try:
        series[0][0]
        return True
    except:
        return False


class MultiSeries:
    def __init__(self, ys, xs=None):
        # Init types
        self.xs: List[np.array] = []
        self.ys: List[np.array] = []

        # First check if the input is multi-dim
        we_have_input_of_multiple_series = _is_multi_dimensional(ys)

        # Initialize y series
        if we_have_input_of_multiple_series:
            self.ys = [np.array(ys_row) for ys_row in ys]
        else:
            self.ys = [np.array(ys)]

        # Initialize x series
        if xs is None:
            self.xs = [
                np.arange(1, len(ys_row) + 1, step=1, dtype=int) for ys_row in self.ys
            ]
        else:
            if we_have_input_of_multiple_series:
                self.xs = [np.array(xs_row) for xs_row in xs]
            else:
                self.xs = [np.array(xs)]

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
