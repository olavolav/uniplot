from typing import Final

import numpy as np
from numpy.typing import NDArray

from uniplot import fill as area_fill

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
    pixels: NDArray | None = None,
    layer: int = 1,
    batch_size: int = BATCH_SIZE,
    fill: float | str | None = None,
):
    if pixels is None:
        pixels = np.zeros((height, width), dtype=np.int32)

    if fill is not None:
        baseline = y_min if fill == "bottom" else float(fill)
        area_fill.render(
            xs, ys, baseline, x_min, x_max, y_min, y_max, pixels, layer, batch_size
        )

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
        if fill is not None:
            valid &= (
                np.isfinite(xs[:-1])
                & np.isfinite(xs[1:])
                & np.isfinite(ys[:-1])
                & np.isfinite(ys[1:])
            )
        xs0 = xs[:-1][valid]
        xs1 = xs[1:][valid]
        ys0 = ys[:-1][valid]
        ys1 = ys[1:][valid]

        for start in range(0, len(xs0), batch_size):
            end = min(start + batch_size, len(xs0))
            x_pairs = np.stack([xs0[start:end], xs1[start:end]], axis=1).reshape(-1)
            y_pairs = np.stack([ys0[start:end], ys1[start:end]], axis=1).reshape(-1)

            line_renderer = (
                _render_batch_of_lines if fill is None else _render_bounded_lines
            )
            pixels = line_renderer(
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
    pixels: NDArray | None = None,
    layer: int = 1,
) -> NDArray:
    if pixels is None:
        pixels = np.zeros((height, width), dtype=np.int32)

    if len(xs) == 0:
        return pixels

    valid = ~np.isnan(xs) & ~np.isnan(ys)
    if width == 1:
        valid &= (xs >= x_min) & (xs <= x_max)
    if height == 1:
        valid &= (ys >= y_min) & (ys <= y_max)

    xs_pix = (width - 1) * (xs[valid] - x_min) / (x_max - x_min)
    ys_pix = (height - 1) * (ys[valid] - y_min) / (y_max - y_min)

    xi = np.round(xs_pix)
    yi = np.round(ys_pix)
    valid = (xi >= 0) & (xi < width) & (yi >= 0) & (yi < height)
    # Reject offscreen values before conversion to avoid integer overflow.
    pixels[height - 1 - yi[valid].astype(int), xi[valid].astype(int)] = layer
    return pixels


def _render_bounded_lines(
    xs, ys, x_min, x_max, y_min, y_max, width, height, pixels, layer=1
):
    """Use the existing sampling grid, restricting steps to visible major pixels."""
    # Preserve visible detail when interpolation would subtract huge endpoints.
    x_margin = (x_max - x_min) / (2 * (width - 1)) if width > 1 else 0
    y_margin = (y_max - y_min) / (2 * (height - 1)) if height > 1 else 0
    x0, x1, y0, y1 = area_fill.clip_extreme_segments(
        xs[::2], xs[1::2], ys[::2], ys[1::2], x_min - x_margin, x_max + x_margin
    )
    y0, y1, x0, x1 = area_fill.clip_extreme_segments(
        y0, y1, x0, x1, y_min - y_margin, y_max + y_margin
    )
    xs = np.stack([x0, x1], axis=1).ravel()
    ys = np.stack([y0, y1], axis=1).ravel()
    # Extended precision keeps projected coordinates finite for extreme inputs.
    if np.any(np.abs(xs) > 1e150) or np.any(np.abs(ys) > 1e150):
        xs, ys = xs.astype(np.longdouble), ys.astype(np.longdouble)
    if width == 1 or height == 1:
        # Clip in data space before a one-pixel dimension collapses coordinates.
        enter = np.zeros(len(xs) // 2)
        leave = np.ones(len(xs) // 2)
        for values, minimum, maximum, size in (
            (xs, x_min, x_max, width),
            (ys, y_min, y_max, height),
        ):
            if size != 1:
                continue
            start, end = values[::2], values[1::2]
            delta = end - start
            parallel = delta == 0
            safe_delta = np.where(parallel, 1, delta)
            first, last = (minimum - start) / safe_delta, (maximum - start) / safe_delta
            enter = np.maximum(enter, np.where(parallel, 0, np.minimum(first, last)))
            leave = np.minimum(leave, np.where(parallel, 1, np.maximum(first, last)))
            leave[parallel & ((start < minimum) | (start > maximum))] = -1
        visible = enter <= leave
        t = np.stack([enter[visible], leave[visible]], axis=1)
        xs = (xs[::2][visible, None] * (1 - t) + xs[1::2][visible, None] * t).ravel()
        ys = (ys[::2][visible, None] * (1 - t) + ys[1::2][visible, None] * t).ravel()
    xp = (width - 1) * (xs - x_min) / (x_max - x_min)
    yp = (height - 1) * (ys - y_min) / (y_max - y_min)
    x0, x1, y0, y1 = xp[::2], xp[1::2], yp[::2], yp[1::2]
    steep = np.abs(y1 - y0) > np.abs(x1 - x0)
    for vertical in (False, True):
        selected = steep == vertical
        a0, a1, b0, b1 = (y0, y1, x0, x1) if vertical else (x0, x1, y0, y1)
        a0, a1, b0, b1 = a0[selected], a1[selected], b0[selected], b1[selected]
        reverse = a0 > a1
        low, high = np.minimum(a0, a1), np.maximum(a0, a1)
        first, last = np.where(reverse, b1, b0), np.where(reverse, b0, b1)
        size = height if vertical else width
        start = np.maximum(np.round(low), 0)
        stop = np.minimum(np.round(low) + np.round(high - low), size - 1)
        visible = (start <= stop) & (high >= -0.5) & (low <= size - 0.5)
        low, high = low[visible], high[visible]
        first, last = first[visible], last[visible]
        start, stop = start[visible], stop[visible]
        if len(start) == 0:
            continue
        counts = (stop - start).astype(int) + 1
        steps = np.arange(counts.max())
        major = start[:, None] + steps
        denominator = high - low
        denominator[abs(denominator) < 1e-10] = 1.0
        t = (major - low[:, None]) / denominator[:, None]
        minor = first[:, None] + t * (last - first)[:, None]
        major = np.clip(major, low[:, None], high[:, None])
        minor = np.clip(
            minor, np.minimum(first, last)[:, None], np.maximum(first, last)[:, None]
        )
        x, y = (minor, major) if vertical else (major, minor)
        x, y = np.round(x), np.round(y)
        valid = (
            (steps < counts[:, None]) & (x >= 0) & (x < width) & (y >= 0) & (y < height)
        )
        pixels[height - 1 - y[valid].astype(int), x[valid].astype(int)] = layer
    return pixels


try:
    from numba import njit, prange  # type: ignore

    @njit(cache=True, fastmath=True, parallel=True)  # type: ignore
    def _render_batch_of_lines(
        xs: NDArray,
        ys: NDArray,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        width: int,
        height: int,
        pixels: NDArray | None = None,
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

        if len(x0) == 0:
            return pixels

        steep = np.abs(y1 - y0) > np.abs(x1 - x0)
        n_lines = len(x0)

        # Step 1: per-line pixel counts (parallel scatter, no shared state)
        counts = np.empty(n_lines, dtype=np.int64)
        for i in prange(n_lines):
            if steep[i]:
                counts[i] = max(1, int(np.round(abs(y1[i] - y0[i]))) + 1)
            else:
                counts[i] = max(1, int(np.round(abs(x1[i] - x0[i]))) + 1)

        # Step 2: prefix sum → per-line start offsets (sequential over lines, not pixels)
        offsets = np.empty(n_lines + 1, dtype=np.int64)
        offsets[0] = 0
        for i in range(n_lines):
            offsets[i + 1] = offsets[i] + counts[i]
        total_pixels = offsets[n_lines]

        # Step 3: allocate output arrays
        x_all = np.empty(total_pixels, dtype=np.float64)
        y_all = np.empty(total_pixels, dtype=np.float64)

        # Step 4: parallel pixel generation — each line writes to its own slice
        for i in prange(n_lines):
            x_start, x_end = x0[i], x1[i]
            y_start, y_end = y0[i], y1[i]
            start = offsets[i]

            if steep[i]:
                if y_start > y_end:
                    y_start, y_end = y_end, y_start
                    x_start, x_end = x_end, x_start

                n = counts[i]
                y_base = np.round(y_start)

                for step in range(n):
                    y_val = y_base + step
                    safe_dy = y_end - y_start
                    if abs(safe_dy) < 1e-10:
                        safe_dy = 1.0
                    t = (y_val - y_start) / safe_dy
                    x_val = x_start + t * (x_end - x_start)

                    y_val = max(min(y_val, max(y_start, y_end)), min(y_start, y_end))
                    x_val = max(min(x_val, max(x_start, x_end)), min(x_start, x_end))

                    x_all[start + step] = x_val
                    y_all[start + step] = y_val
            else:
                if x_start > x_end:
                    x_start, x_end = x_end, x_start
                    y_start, y_end = y_end, y_start

                n = counts[i]
                x_base = np.round(x_start)

                for step in range(n):
                    x_val = x_base + step
                    safe_dx = x_end - x_start
                    if abs(safe_dx) < 1e-10:
                        safe_dx = 1.0
                    t = (x_val - x_start) / safe_dx
                    y_val = y_start + t * (y_end - y_start)

                    x_val = max(min(x_val, max(x_start, x_end)), min(x_start, x_end))
                    y_val = max(min(y_val, max(y_start, y_end)), min(y_start, y_end))

                    x_all[start + step] = x_val
                    y_all[start + step] = y_val

        # Step 5: parallel pixel write — benign race: constant value, last writer wins
        for i in prange(total_pixels):
            xi = int(np.round(x_all[i]))
            yi = height - 1 - int(np.round(y_all[i]))
            if 0 <= xi < width and 0 <= yi < height:
                pixels[yi, xi] = layer

        return pixels

except ImportError:

    def _render_batch_of_lines(  # type: ignore[misc]
        xs: NDArray,
        ys: NDArray,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        width: int,
        height: int,
        pixels: NDArray | None = None,
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

        if len(x0) == 0:
            return pixels

        steep = np.abs(y1 - y0) > np.abs(x1 - x0)

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
