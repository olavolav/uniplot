"""
A collection of functions for discretizing continuous data.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Any

from uniplot.conversions import floatify


def discretize(x: Any, x_min: float, x_max: float, steps: int) -> int:
    """
    Returns a discretized integer.
    """
    return int(((floatify(x) - x_min) / (x_max - x_min)) * steps)


def discretize_array(x: NDArray, x_min: float, x_max: float, steps: int) -> NDArray:
    """
    Returns a NumPy array of discretized integer values. NaN values will return
    -1.

    Note that the integer values are not bound to the rande defined by `steps`.
    """
    array = ((np.asarray(x).astype(float) - x_min) / (x_max - x_min)) * steps
    return np.nan_to_num(array, nan=-1).astype(int)


def compute_y_at_middle_of_row(
    height_index_from_top: int, y_min: float, y_max: float, height: int
) -> float:
    """
    Returns the y level at the middle of the specified bin.

    Typical use case is to display the right axis tick.
    """
    return invert_discretize(
        i=height - height_index_from_top - 1,
        minimum=y_min,
        maximum=y_max,
        nr_bins=height,
    )


def invert_discretize(i: int, minimum: float, maximum: float, nr_bins: int) -> float:
    """
    Returns the level at the middle of the specified bin.

    This is the inverse of `discretizer.discretize`.
    """
    assert maximum > minimum

    step_size = (maximum - minimum) / nr_bins
    return float((i + 0.5) * step_size + minimum)


def invert_discretize_array(
    i: NDArray, minimum: float, maximum: float, nr_bins: int
) -> NDArray:
    """
    Returns the level at the middle of the specified bin.

    This is the inverse of `discretizer.discretize`.
    """
    assert maximum > minimum

    step_size = (maximum - minimum) / nr_bins
    return ((np.asarray(i).astype(float) + 0.5) * step_size + minimum).astype(float)
