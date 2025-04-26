import numpy as np
from numpy.typing import NDArray
from typing import Optional, Final


BATCH_SIZE: Final = 10_000


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
    batch_size: int = BATCH_SIZE,
):
    if pixels is None:
        pixels = np.zeros((height, width), dtype=np.int32)

    # Always render points
    for start in range(0, len(xs), batch_size):
        end = min(start + batch_size, len(xs))
        pixels = _render_batch_of_dots(
            xs=xs[start:end],
            ys=ys[start:end],
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            width=width,
            height=height,
            pixels=pixels,
            layer=layer,
        )

    # Optionally render lines
    if lines and len(xs) >= 2:
        valid = (
            ~np.isnan(xs[:-1])
            & ~np.isnan(xs[1:])
            & ~np.isnan(ys[:-1])
            & ~np.isnan(ys[1:])
        )
        xs0 = xs[:-1][valid]
        xs1 = xs[1:][valid]
        ys0 = ys[:-1][valid]
        ys1 = ys[1:][valid]

        for start in range(0, len(xs0), batch_size):
            end = min(start + batch_size, len(xs0))
            x_pairs = np.stack([xs0[start:end], xs1[start:end]], axis=1).reshape(-1)
            y_pairs = np.stack([ys0[start:end], ys1[start:end]], axis=1).reshape(-1)

            pixels = _render_batch_of_lines(
                xs=x_pairs,
                ys=y_pairs,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                width=width,
                height=height,
                pixels=pixels,
                layer=layer,
            )

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


###########
# private #
###########


def _render_batch_of_dots(
    xs: NDArray,
    ys: NDArray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    pixels: Optional[NDArray] = None,
    layer: int = 1,
) -> NDArray:
    if pixels is None:
        pixels = np.zeros((height, width), dtype=np.int32)

    if len(xs) == 0:
        return pixels

    valid = ~np.isnan(xs) & ~np.isnan(ys)

    xs_pix = (width - 1) * (xs[valid] - x_min) / (x_max - x_min)
    ys_pix = (height - 1) * (ys[valid] - y_min) / (y_max - y_min)

    xi = np.round(xs_pix).astype(int)
    yi = np.round(ys_pix).astype(int)
    yi = height - 1 - yi  # flip Y for image coordinates
    valid = (
        (~np.isnan(xi))
        & (xi >= 0)
        & (xi < width)
        & (~np.isnan(yi))
        & (yi >= 0)
        & (yi < height)
    )
    pixels[yi[valid], xi[valid]] = layer
    return pixels


def _render_batch_of_lines(
    xs: NDArray,
    ys: NDArray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    pixels: Optional[NDArray] = None,
    layer: int = 1,
) -> NDArray:
    if pixels is None:
        pixels = np.zeros((height, width), dtype=np.int32)

    if len(xs) == 0:
        return pixels

    xs_pix = (width - 1) * (xs - x_min) / (x_max - x_min)
    ys_pix = (height - 1) * (ys - y_min) / (y_max - y_min)

    x0, x1 = xs_pix[::2], xs_pix[1::2]
    y0, y1 = ys_pix[::2], ys_pix[1::2]

    valid = ~np.isnan(x0) & ~np.isnan(x1) & ~np.isnan(y0) & ~np.isnan(y1)
    x0, x1 = x0[valid], x1[valid]
    y0, y1 = y0[valid], y1[valid]

    dx = x1 - x0
    dy = y1 - y0
    steep = np.abs(dy) > np.abs(dx)

    all_x, all_y = [], []

    # Shallow lines
    mask = ~steep
    if np.any(mask):
        x0s, x1s = x0[mask], x1[mask]
        y0s, y1s = y0[mask], y1[mask]

        swap = x0s > x1s
        x0s[swap], x1s[swap] = x1s[swap], x0s[swap]
        y0s[swap], y1s[swap] = y1s[swap], y0s[swap]

        n = np.maximum(np.round(x1s - x0s).astype(int) + 1, 1)
        steps = np.arange(n.max())
        steps = steps[None, :] * np.ones((len(n), 1))
        mask_steps = steps < n[:, None]

        x_vals = np.round(x0s)[:, None] + steps
        safe_dx = x1s - x0s
        safe_dx[safe_dx == 0] = 1
        t = (x_vals - x0s[:, None]) / safe_dx[:, None]
        y_vals = y0s[:, None] + t * (y1s - y0s)[:, None]

        x_vals = np.clip(
            x_vals,
            np.minimum(x0s[:, None], x1s[:, None]),
            np.maximum(x0s[:, None], x1s[:, None]),
        )
        y_vals = np.clip(
            y_vals,
            np.minimum(y0s[:, None], y1s[:, None]),
            np.maximum(y0s[:, None], y1s[:, None]),
        )

        all_x.append(x_vals[mask_steps])
        all_y.append(y_vals[mask_steps])

    # Steep lines
    mask = steep
    if np.any(mask):
        x0s, x1s = x0[mask], x1[mask]
        y0s, y1s = y0[mask], y1[mask]

        swap = y0s > y1s
        x0s[swap], x1s[swap] = x1s[swap], x0s[swap]
        y0s[swap], y1s[swap] = y1s[swap], y0s[swap]

        n = np.maximum(np.round(y1s - y0s).astype(int) + 1, 1)
        steps = np.arange(n.max())
        steps = steps[None, :] * np.ones((len(n), 1))
        mask_steps = steps < n[:, None]

        y_vals = np.round(y0s)[:, None] + steps
        safe_dy = y1s - y0s
        safe_dy[safe_dy == 0] = 1
        t = (y_vals - y0s[:, None]) / safe_dy[:, None]
        x_vals = x0s[:, None] + t * (x1s - x0s)[:, None]

        y_vals = np.clip(
            y_vals,
            np.minimum(y0s[:, None], y1s[:, None]),
            np.maximum(y0s[:, None], y1s[:, None]),
        )
        x_vals = np.clip(
            x_vals,
            np.minimum(x0s[:, None], x1s[:, None]),
            np.maximum(x0s[:, None], x1s[:, None]),
        )

        all_x.append(x_vals[mask_steps])
        all_y.append(y_vals[mask_steps])

    if not all_x:
        return pixels

    x_all = np.round(np.concatenate(all_x)).astype(int)
    y_all = np.round(np.concatenate(all_y)).astype(int)
    y_all = height - 1 - y_all

    valid = (x_all >= 0) & (x_all < width) & (y_all >= 0) & (y_all < height)
    pixels[y_all[valid], x_all[valid]] = layer

    return pixels
