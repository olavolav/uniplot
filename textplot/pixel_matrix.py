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

    pixels = np.zeros((width, height), dtype=int)

    for i in range(len(ys)):
        # TODO Optimize as vector operations
        x_pixel = _discretize(xs[i], x_min, x_max, steps=width)
        y_pixel = _discretize(ys[i], y_min, y_max, steps=height)

        if x_pixel is not None and y_pixel is not None:
            pixels[x_pixel, height - 1 - y_pixel] = 1

    return pixels


###########
# private #
###########


def _discretize(x: float, x_min: float, x_max: float, steps: int) -> Optional[int]:
    """
    Returns a discretized integer between 0 and `steps-1`, or None if the `x` value is outside of the given range.
    """
    if x < x_min or x >= x_max:
        return None
    return int(((x - x_min) / (x_max - x_min)) * steps)
