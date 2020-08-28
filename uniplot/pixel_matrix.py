import numpy as np  # type: ignore
from typing import Optional

from uniplot.discretizer import discretize


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

    x_indices = discretize(np.array(xs), x_min, x_max, steps=width)
    y_indices = discretize(np.array(ys), y_min, y_max, steps=height)

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


# def merge_on_top_with_shadow(
#     low_layer: np.array, high_layer: np.array, width: int, height: int
# ) -> np.array:
#     """
#     Put a pixel matrix on top of another, with a single solid line of "shadow",
#     including diagonal fields.
#
#     This shadow will ensure that later 2x2 squares exclusively belong to one particular
#     line.
#     """
#     merged_layer = bottom_layer
#
#     for row in range(height):
#         for col in range(width):
#             if high_layer[row, col] != 0:
#                 # Overwrite bottom with top value
#                 merged_layer[row, col] = high_layer[row, col]
#             elif low_layer[row, col] != 0:
#                 # Check if we should set this pixel to zero because of shadowing
#                 if not _check_surrounding_is_blank():
#                     merged_layer[row, col] = 0
#
#     return merged_layer
