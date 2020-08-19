import numpy as np  # type: ignore
from typing import Optional


def render(
    xs: np.array,
    ys: np.array,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
) -> np.array:
    """
    Turn a list of 2D points into a raster matrix.

    Returns the pixels as 2D array with 1 or 0 integer entries.

    Note that the row order is optimized for drawing later, so the first row corresponds
    to the highest line of pixels.
    """
    assert len(xs) == len(ys)
    assert x_max > x_min
    assert y_max > y_min
    assert width > 0
    assert height > 0

    x_indices = _discretize_array(np.array(xs), x_min, x_max, steps=width)
    y_indices = _discretize_array(np.array(ys), y_min, y_max, steps=height)

    # Invert y direction to optimize for plotting later
    y_indices = (height - 1) - y_indices

    # Filter out of view pixels
    xy_indices = np.stack((x_indices, y_indices)).T
    xy_indices = xy_indices[
        (xy_indices[:, 0] >= 0)
        & (xy_indices[:, 0] < width)
        & (xy_indices[:, 1] >= 0)
        & (xy_indices[:, 1] < height)
    ]
    xy_indices = xy_indices.T

    # Assemble pixel matrix
    pixels = np.zeros((height, width), dtype=int)
    pixels[xy_indices[1], xy_indices[0]] = 1

    return pixels


###########
# private #
###########


def _discretize_array(x: np.array, x_min: float, x_max: float, steps: int) -> np.array:
    """
    Returns an array with discretized integers between 0 and `steps-1`.
    """
    return (((x - x_min) / (x_max - x_min)) * steps).astype(int)
