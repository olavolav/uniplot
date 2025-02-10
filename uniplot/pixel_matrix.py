import numpy as np
from numpy.typing import NDArray
from typing import Optional

from uniplot.discretizer import (
    discretize_array,
    invert_discretize_array,
)


def render(
    xs: NDArray,
    ys: NDArray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    lines: bool = False,
) -> NDArray:
    """
    Turn a list of 2D points into a raster matrix.

    Returns the pixels as 2D array with 1 or 0 integer entries.

    Note that the row order is optimized for drawing later, so the first row
    corresponds to the highest line of pixels.
    """
    xs = np.array(xs)
    ys = np.array(ys)

    assert xs.shape == ys.shape
    assert x_max > x_min
    assert y_max > y_min
    assert width > 0
    assert height > 0

    pixels = np.zeros((height, width), dtype=int)

    x_indices = discretize_array(xs, x_min, x_max, steps=width)
    y_indices = discretize_array(ys, y_min, y_max, steps=height)

    # Invert y direction to optimize for plotting later
    y_indices = (height - 1) - y_indices

    # Combine lists to get coordinates
    xy_indices = np.column_stack((x_indices, y_indices))

    if lines:
        xys = np.column_stack((xs, ys))

        # Compute all line segments as an array with entries of the shape:
        # [
        #     [x_index_start, y_index_start],
        #     [x_start, y_start],
        #     [x_index_stop, y_index_stop],
        #     [x_stop, y_stop]
        # ]
        xy_line_endpoints = np.stack(
            (xy_indices[:-1], xys[:-1], xy_indices[1:], xys[1:]), axis=1
        ).astype(float)

        # Filter any line segments where any coordinatwe is NaN
        xy_line_endpoints = xy_line_endpoints[
            ~np.isnan(xy_line_endpoints).any(axis=2).any(axis=1)
        ]

        # Filter out of view line segments
        xy_line_endpoints = xy_line_endpoints[
            (
                # At least one of the x coordinates of start and end need to be
                # >= x_min
                (xy_line_endpoints[:, 1, 0] >= x_min)
                | (xy_line_endpoints[:, 3, 0] >= x_min)
            )
            & (
                # At least one of the x coordinates of start and end need to be
                # < x_max
                (xy_line_endpoints[:, 1, 0] < x_max)
                | (xy_line_endpoints[:, 3, 0] < x_max)
            )
            & (
                # At least one of the y coordinates of start and end need to be
                # >= y_min
                (xy_line_endpoints[:, 1, 1] >= y_min)
                | (xy_line_endpoints[:, 3, 1] >= y_min)
            )
            & (
                # At least one of the y coordinates of start and end need to be
                # < x_max
                (xy_line_endpoints[:, 1, 1] < y_max)
                | (xy_line_endpoints[:, 3, 1] < y_max)
            )
            & (
                # The start and stop indices need to be different by at least 2
                # in any direction
                (np.abs(xy_line_endpoints[:, 0, 0] - xy_line_endpoints[:, 2, 0]) > 1.5)
                | (
                    np.abs(xy_line_endpoints[:, 0, 1] - xy_line_endpoints[:, 2, 1])
                    > 1.5
                )
            )
        ]

        # TODO This can likely be optimized by assembling all segments and
        # computing the pixels of all lines together, or at least of each half
        # split by slope for segment in np.nditer(xy_line_endpoints)
        x_indices_of_line: NDArray = np.array([])
        y_indices_of_line: NDArray = np.array([])
        indices_slope: Optional[float] = None
        slope: Optional[float] = None
        for [
            [x_index_start, y_index_start],
            [x_start, y_start],
            [x_index_stop, y_index_stop],
            [x_stop, y_stop],
        ] in xy_line_endpoints:
            # Convert back to integers (not very efficient)
            x_index_start = int(round(x_index_start))
            x_index_stop = int(round(x_index_stop))
            y_index_start = int(round(y_index_start))
            y_index_stop = int(round(y_index_stop))

            # For convenience
            x_index_smaller = min(x_index_start, x_index_stop)
            x_index_bigger = max(x_index_start, x_index_stop)
            y_index_smaller = min(y_index_start, y_index_stop)
            y_index_bigger = max(y_index_start, y_index_stop)

            # Slope is inverted because y indices are inverted
            indices_slope = None
            if x_index_start != x_index_stop:
                indices_slope = (
                    -1 * (y_index_stop - y_index_start) / (x_index_stop - x_index_start)
                )
            slope = None
            if x_start != x_stop:
                slope = (y_stop - y_start) / (x_stop - x_start)

            if indices_slope is None:
                # That means it's a vertical line
                pixels[
                    max(y_index_smaller, 0) : max(y_index_bigger, 0), x_index_start
                ] = 1
                continue

            if y_index_start == y_index_stop:
                # That means it's a horizontal line
                pixels[
                    y_index_start, max(x_index_smaller, 0) : max(x_index_bigger, 0)
                ] = 1
                continue

            if abs(indices_slope) > 1:
                # Draw line by iterating vertically:
                # 1. Compute y indices in the middle of bins between the two
                # origins
                step = 1
                if y_index_stop < y_index_start:
                    step = -1
                y_indices_of_line = np.arange(
                    y_index_start, y_index_stop + step, step=step
                )
                ys_of_line = invert_discretize_array(
                    height - 1 - y_indices_of_line,
                    minimum=y_min,
                    maximum=y_max,
                    nr_bins=height,
                )

                # 2. Compute corresponding x coordinates
                # Derivation:
                #   xs_of_line - x_start = (ys_of_line - y_start) / slope
                #   xs_of_line = (ys_of_line - y_start) / slope + x_start
                xs_of_line = (ys_of_line - y_start) / slope + x_start
                x_indices_of_line = discretize_array(
                    xs_of_line, x_min=x_min, x_max=x_max, steps=width
                )

            else:
                # Draw line by iterating horizontically:
                # 1. Compute x indices in the middle of bins between the two
                # origins
                step = 1
                if x_index_stop < x_index_start:
                    step = -1
                x_indices_of_line = np.arange(
                    x_index_start, x_index_stop + step, step=step
                )
                xs_of_line = invert_discretize_array(
                    x_indices_of_line, minimum=x_min, maximum=x_max, nr_bins=width
                )

                # 2. Compute corresponding y coordinates
                ys_of_line = y_start + slope * (xs_of_line - x_start)
                y_indices_of_line = (
                    height
                    - 1
                    - discretize_array(
                        ys_of_line, x_min=y_min, x_max=y_max, steps=height
                    )
                )

            # Assemble pixels
            xy_indices_of_line = np.column_stack((x_indices_of_line, y_indices_of_line))

            # Filter out of view pixels
            xy_indices_of_line = xy_indices_of_line[
                (xy_indices_of_line[:, 0] >= max(0, x_index_smaller))
                & (xy_indices_of_line[:, 0] <= min(width - 1, x_index_bigger))
                & (xy_indices_of_line[:, 1] >= max(0, y_index_smaller))
                & (xy_indices_of_line[:, 1] <= min(height - 1, y_index_bigger))
            ]
            xy_indices_of_line = xy_indices_of_line.T
            pixels[xy_indices_of_line[1], xy_indices_of_line[0]] = 1

    # Filter out NaN and out of view pixels
    xy_indices = xy_indices[
        (xy_indices[:, 0] >= 0)
        & (xy_indices[:, 0] < width)
        & (xy_indices[:, 1] >= 0)
        & (xy_indices[:, 1] < height)
    ]
    xy_indices = xy_indices.T

    # Assemble pixel matrix
    pixels[xy_indices[1], xy_indices[0]] = 1

    return pixels


def merge_on_top(
    low_layer: NDArray,
    high_layer: NDArray,
    width: int,
    height: int,
    with_shadow: bool = False,
) -> NDArray:
    """
    Put a pixel matrix on top of another, with an optional single solid line of
    "shadow", including diagonal fields.

    If activated, this shadow will ensure that later 2x2 squares exclusively
    belong to one particular line.
    """
    merged_layer = np.copy(low_layer)

    not_zero_high_layer = high_layer != 0
    merged_layer[not_zero_high_layer] = high_layer[not_zero_high_layer]

    if with_shadow:  # deprecated? 
        # can be also vectorized if is in use
        for row in range(height):
            for col in range(width):
                if merged_layer[row, col] != 0:
                    # So we know that the top layer at position `[row, col]` is
                    # blank but the bottom one is not. So now we check if we should
                    # set this pixel to zero because of shadowing.
                    if (
                        high_layer[
                            max(row - 1, 0) : min(row + 2, height),
                            max(col - 1, 0) : min(col + 2, width),
                        ]
                        > 0
                    ).any():
                        # Apply shadow
                        merged_layer[row, col] = 0

    return merged_layer
