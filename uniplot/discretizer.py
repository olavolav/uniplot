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
    step_size = (y_max - y_min) / height
    return (height - (height_index_from_top + 0.5)) * step_size + y_min
