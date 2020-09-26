import numpy as np  # type: ignore
from typing import Optional

from uniplot.discretizer import discretize, invert_discretize


def render(
    xs: np.array,
    ys: np.array,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    lines: bool = False,
) -> np.array:
    """
    Turn a list of 2D points into a raster matrix.

    Returns the pixels as 2D array with 1 or 0 integer entries.

    Note that the row order is optimized for drawing later, so the first row corresponds
    to the highest line of pixels.
    """
    xs = np.array(xs)
    ys = np.array(ys)

    assert xs.shape == ys.shape
    assert x_max > x_min
    assert y_max > y_min
    assert width > 0
    assert height > 0

    pixels = np.zeros((height, width), dtype=int)

    x_indices = discretize(xs, x_min, x_max, steps=width)
    y_indices = discretize(ys, y_min, y_max, steps=height)

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
        )

        # TODO Sort list, to have good assumptions for later

        # TODO Filter out of view line segments

        # TODO This can likely be optimized by assembling all segments and computing the
        # pixels of all lines together, or at least of each half split by slope
        # print("DEBUG: xy_line_endpoints = ", xy_line_endpoints)
        # for segment in np.nditer(xy_line_endpoints): # TODO use this
        for segment in xy_line_endpoints:
            # print("DEBUG: segment = ", segment)
            [
                [x_index_start, y_index_start],
                [x_start, y_start],
                [x_index_stop, y_index_stop],
                [x_stop, y_stop],
            ] = segment

            # Slope is inverted because y indices are inverted
            # indices_slope = (
            #     -1 * (y_index_stop - y_index_start) / (x_index_stop - x_index_start)
            # )
            # print("DEBUG: indices_slope = ", indices_slope)
            slope = (y_stop - y_start) / (x_stop - x_start)
            print("DEBUG: slope = ", slope)

            # Skip those segments where there is no space anyway between the points
            if (
                abs(x_index_stop - x_index_start) < 2
                and abs(y_index_stop - y_index_start) < 2
            ):
                continue

            # if indices_slope > 0.5: # TODO
            #     # Draw line by iterating vertically
            #     pass
            # else:

            # Draw line by iterating horizontically
            # 1. Compute x indices in the middle of bins between the two origins
            x_indices_of_line = np.arange(x_index_start + 1, x_index_stop)
            print("DEBUG: x_indices_of_line = ", x_indices_of_line)
            xs_of_line = invert_discretize(
                x_indices_of_line, minimum=x_min, maximum=x_max, nr_bins=width
            )
            print("DEBUG: xs_of_line = ", xs_of_line)

            # 2. Compute corresponding y coordinates
            ys_of_line = y_start + slope * (xs_of_line - x_start)
            print("DEBUG: ys_of_line = ", ys_of_line)
            y_indices_of_line = (
                height
                - 1
                - discretize(ys_of_line, x_min=y_min, x_max=y_max, steps=height)
            )
            print("DEBUG: y_indices_of_line = ", y_indices_of_line)

            # 3. Draw pixels
            xy_indices_of_line = np.column_stack((x_indices_of_line, y_indices_of_line))
            print("DEBUG: xy_indices_of_line = ", xy_indices_of_line)

            # Filter out of view pixels
            # TODO DRY
            xy_indices_of_line = xy_indices_of_line[
                (xy_indices_of_line[:, 0] >= 0)
                & (xy_indices_of_line[:, 0] < width)
                & (xy_indices_of_line[:, 1] >= 0)
                & (xy_indices_of_line[:, 1] < height)
            ]
            xy_indices_of_line = xy_indices_of_line.T
            pixels[xy_indices_of_line[1], xy_indices_of_line[0]] = 1

    # Filter out of view pixels
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
    low_layer: np.array,
    high_layer: np.array,
    width: int,
    height: int,
    with_shadow: bool = False,
) -> np.array:
    """
    Put a pixel matrix on top of another, with an optional single solid line of "shadow",
    including diagonal fields.

    If activated, this shadow will ensure that later 2x2 squares exclusively belong to
    one particular line.
    """
    merged_layer = np.copy(low_layer)

    for row in range(height):
        for col in range(width):
            if high_layer[row, col] != 0:
                # Overwrite bottom with top value
                merged_layer[row, col] = high_layer[row, col]
            elif with_shadow and merged_layer[row, col] != 0:
                # So we know that the top layer at position `[row, col]` is blank but
                # the bottom one is not. So now we check if we should set this pixel to
                # zero because of shadowing.
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
