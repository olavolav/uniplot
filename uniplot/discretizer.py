"""
A collection of functions for discretizing continuous data.
"""

import numpy as np  # type: ignore
from typing import Union


def discretize(
    x: Union[float, np.array], x_min: float, x_max: float, steps: int
) -> Union[int, np.array]:
    """
    Returns a discretized integer.
    """
    return (((np.asarray(x) - x_min) / (x_max - x_min)) * steps).astype(int)


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


def invert_discretize(
    i: Union[int, np.array], minimum: float, maximum: float, nr_bins: int
) -> Union[int, np.array]:
    """
    Returns the level at the middle of the specified bin.

    This is the inverse of `discretizer.discretize`.
    """
    assert maximum > minimum

    step_size = (maximum - minimum) / nr_bins
    return ((np.asarray(i) + 0.5) * step_size + minimum).astype(float)
