import numpy as np
from numpy.typing import NDArray
from typing import Optional


BATCH_SIZE = 500_000  # Set the batch size for processing


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
    pixels: Optional[NDArray] = None,
    layer: int = 1,
) -> NDArray:
    # Initialize the pixels array if not provided
    if pixels is None:
        pixels = np.zeros((height, width), dtype=int)

    # Process data in batches
    for start_idx in range(0, len(xs), BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, len(xs))
        xs_batch = xs[start_idx:end_idx]
        ys_batch = ys[start_idx:end_idx]

        # Call the original render function for this batch
        pixels = render_batch(
            xs=xs_batch,
            ys=ys_batch,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            width=width,
            height=height,
            lines=lines,
            pixels=pixels,  # Keep the same pixels array to accumulate results
            layer=layer,
        )

    return pixels


def render_batch(
    xs: NDArray,
    ys: NDArray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    lines: bool = False,
    pixels: Optional[NDArray] = None,
    layer: int = 1,
) -> NDArray:
    """
    Render 2D points or line segments to a raster image.

    Coordinate system:
    - (x_min, y_min) is the bottom-left of the plot area.
    - (x_max, y_max) is the top-right of the plot area.
    - The output array uses image-style coordinates:
        - [0, 0] is the top-left corner.
        - Y increases downward.
    """
    if pixels is None:
        pixels = np.zeros((height, width), dtype=int)

    if len(xs) == 0:
        return pixels

    # Normalize coordinates to pixel indices
    xs_pix = (width - 1) * (xs - x_min) / (x_max - x_min)
    ys_pix = (height - 1) * (ys - y_min) / (y_max - y_min)

    if not lines:
        xi = np.round(xs_pix).astype(int)
        yi = np.round(ys_pix).astype(int)
        yi = height - 1 - yi  # flip Y
        valid = (xi >= 0) & (xi < width) & (yi >= 0) & (yi < height)
        pixels[yi[valid], xi[valid]] = layer  # Set pixels to layer value directly
        return pixels

    # Filter out lines with NaNs
    mask = (
        (~np.isnan(xs_pix[:-1]))
        & (~np.isnan(xs_pix[1:]))
        & (~np.isnan(ys_pix[:-1]))
        & (~np.isnan(ys_pix[1:]))
    )
    x0 = xs_pix[:-1][mask]
    y0 = ys_pix[:-1][mask]
    x1 = xs_pix[1:][mask]
    y1 = ys_pix[1:][mask]

    dx = x1 - x0
    dy = y1 - y0

    steep = np.abs(dy) > np.abs(dx)

    all_x, all_y = [], []

    shallow_mask = ~steep
    if np.any(shallow_mask):
        x0s = x0[shallow_mask].copy()
        x1s = x1[shallow_mask].copy()
        y0s = y0[shallow_mask].copy()
        y1s = y1[shallow_mask].copy()

        swap_mask = x0s > x1s
        x0s[swap_mask], x1s[swap_mask] = x1s[swap_mask], x0s[swap_mask]
        y0s[swap_mask], y1s[swap_mask] = y1s[swap_mask], y0s[swap_mask]

        n = np.maximum(np.ceil(x1s - x0s).astype(int) + 1, 2)
        steps = np.arange(n.max())
        steps = steps[None, :] * np.ones((len(n), 1))
        mask = steps < n[:, None]
        x_vals = x0s[:, None] + (steps * (x1s - x0s)[:, None] / (n - 1)[:, None])
        y_vals = y0s[:, None] + (steps * (y1s - y0s)[:, None] / (n - 1)[:, None])
        all_x.append(x_vals[mask])
        all_y.append(y_vals[mask])

    if np.any(steep):
        x0s = x0[steep].copy()
        x1s = x1[steep].copy()
        y0s = y0[steep].copy()
        y1s = y1[steep].copy()

        swap_mask = y0s > y1s
        x0s[swap_mask], x1s[swap_mask] = x1s[swap_mask], x0s[swap_mask]
        y0s[swap_mask], y1s[swap_mask] = y1s[swap_mask], y0s[swap_mask]

        n = np.maximum(np.ceil(y1s - y0s).astype(int) + 1, 2)
        steps = np.arange(n.max())
        steps = steps[None, :] * np.ones((len(n), 1))
        mask = steps < n[:, None]
        y_vals = y0s[:, None] + (steps * (y1s - y0s)[:, None] / (n - 1)[:, None])
        x_vals = x0s[:, None] + (steps * (x1s - x0s)[:, None] / (n - 1)[:, None])
        all_x.append(x_vals[mask])
        all_y.append(y_vals[mask])

    if not all_x:
        return pixels

    x_all = np.round(np.concatenate(all_x)).astype(int)
    y_all = np.round(np.concatenate(all_y)).astype(int)

    y_all = height - 1 - y_all  # flip y

    valid = (x_all >= 0) & (x_all < width) & (y_all >= 0) & (y_all < height)
    x_all = x_all[valid]
    y_all = y_all[valid]

    # Set pixels to the layer value directly for valid positions
    pixels[y_all, x_all] = layer

    return pixels


def merge_on_top(
    low_layer: NDArray, high_layer: NDArray, width: int, height: int
) -> NDArray:
    """
    Put a pixel matrix on top of another, with an optional single solid line of
    "shadow", including diagonal fields.

    If activated, this shadow will ensure that later 2x2 squares exclusively
    belong to one particular line.

    TODO I stopped using this but still there is the unused shadow stuff,
    I would delete it as well as the tests
    """
    merged_layer = np.copy(low_layer)

    not_zero_high_layer = high_layer != 0
    merged_layer[not_zero_high_layer] = high_layer[not_zero_high_layer]

    return merged_layer
