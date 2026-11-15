"""Rasterize unions of segment areas using viewport-sized column intervals."""

import numpy as np
from numpy.typing import NDArray


def _render_numpy(x0, x1, y0, y1, baseline, edges, y_min, y_max):
    lower = np.full(len(edges) - 1, np.inf)
    upper = np.full(len(edges) - 1, -np.inf)
    if len(x0) == 0:
        return lower, upper
    start = max(0, np.searchsorted(edges, x0.min(), side="right") - 1)
    stop = min(len(lower), np.searchsorted(edges, x1.max(), side="left"))
    # Batch-sized arrays only; no segment-by-pixel temporary matrix.
    for column in range(start, stop):
        selected = (x0 < edges[column + 1]) & (x1 > edges[column])
        a, b = x0[selected], x1[selected]
        c, d = y0[selected], y1[selected]
        if len(a) == 0:
            continue
        left = np.maximum(a, edges[column])
        right = np.minimum(b, edges[column + 1])
        magnitude = np.maximum(np.abs(a), np.abs(b))
        scale = np.where(magnitude > 1e150, magnitude, 1.0)
        # Scale only huge endpoints. Scaling nearby timestamps loses precision.
        denominator = b / scale - a / scale
        t0 = np.clip((left / scale - a / scale) / denominator, 0, 1)
        t1 = np.clip((right / scale - a / scale) / denominator, 0, 1)
        first = c * (1 - t0) + d * t0
        last = c * (1 - t1) + d * t1
        low = np.maximum(np.minimum(np.minimum(first, last), baseline), y_min)
        high = np.minimum(np.maximum(np.maximum(first, last), baseline), y_max)
        visible = low < high
        if np.any(visible):
            lower[column] = low[visible].min()
            upper[column] = high[visible].max()
    return lower, upper


try:
    from numba import njit  # type: ignore[import-not-found, import-untyped]

    @njit(cache=True)
    def _render_numba(x0, x1, y0, y1, baseline, edges, y_min, y_max):
        lower = np.full(len(edges) - 1, np.inf)
        upper = np.full(len(edges) - 1, -np.inf)
        # Serial reduction avoids races on shared extrema. Each segment visits
        # only the columns it intersects, including subpixel-width segments.
        for i in range(len(x0)):
            start = max(0, np.searchsorted(edges, x0[i], side="right") - 1)
            stop = min(len(lower), np.searchsorted(edges, x1[i], side="left"))
            magnitude = max(abs(x0[i]), abs(x1[i]))
            scale = magnitude if magnitude > 1e150 else 1.0
            denominator = x1[i] / scale - x0[i] / scale
            for column in range(start, stop):
                left = max(x0[i], edges[column])
                right = min(x1[i], edges[column + 1])
                t0 = min(1.0, max(0.0, (left / scale - x0[i] / scale) / denominator))
                t1 = min(1.0, max(0.0, (right / scale - x0[i] / scale) / denominator))
                first = y0[i] * (1 - t0) + y1[i] * t0
                last = y0[i] * (1 - t1) + y1[i] * t1
                low = max(min(first, last, baseline), y_min)
                high = min(max(first, last, baseline), y_max)
                if low < high:
                    lower[column] = min(lower[column], low)
                    upper[column] = max(upper[column], high)
        return lower, upper

except ImportError:
    _render_numba = None  # type: ignore[assignment]

_render = _render_numba if _render_numba is not None else _render_numpy


def _cell_edges(minimum: float, maximum: float, size: int) -> NDArray:
    centers = np.linspace(minimum, maximum, size)
    return np.r_[minimum, centers[:-1] / 2 + centers[1:] / 2, maximum]


def render(xs, ys, baseline, x_min, x_max, y_min, y_max, pixels, layer, batch_size):
    """Paint positive-area pixel overlaps, retaining existing pixel ownership."""
    height, width = pixels.shape
    x_edges = _cell_edges(x_min, x_max, width)
    y_edges = _cell_edges(y_min, y_max, height)
    lower = np.full(width, np.inf)
    upper = np.full(width, -np.inf)
    for start in range(0, len(xs) - 1, batch_size):
        stop = min(start + batch_size, len(xs) - 1)
        a, b = xs[start:stop], xs[start + 1 : stop + 1]
        c, d = ys[start:stop], ys[start + 1 : stop + 1]
        valid = (
            np.isfinite(a)
            & np.isfinite(b)
            & np.isfinite(c)
            & np.isfinite(d)
            & (a != b)
            & ((c != baseline) | (d != baseline))
            & (np.maximum(a, b) > x_min)
            & (np.minimum(a, b) < x_max)
            & (np.maximum(np.maximum(c, d), baseline) > y_min)
            & (np.minimum(np.minimum(c, d), baseline) < y_max)
        )
        a, b, c, d = a[valid], b[valid], c[valid], d[valid]
        a, b, c, d = clip_extreme_segments(a, b, c, d, x_min, x_max)
        forward = a < b
        batch_lower, batch_upper = _render(
            np.minimum(a, b),
            np.maximum(a, b),
            np.where(forward, c, d),
            np.where(forward, d, c),
            baseline,
            x_edges,
            y_min,
            y_max,
        )
        np.minimum(lower, batch_lower, out=lower)
        np.maximum(upper, batch_upper, out=upper)
    covered = (lower[None, :] < y_edges[1:, None]) & (
        upper[None, :] > y_edges[:-1, None]
    )
    pixels[covered[::-1]] = layer


def clip_extreme_segments(x0, x1, y0, y1, minimum, maximum):
    """Clip unusually distant endpoints before float interpolation loses detail.

    Decimal is used only for spans over a trillion times the viewport scale.
    Its precision covers the full exponent range of finite float64 inputs.
    Normal segments retain their original coordinates and sampling phase.
    """
    scale = max(abs(minimum), abs(maximum), maximum - minimum, 1.0)
    distant = np.maximum(np.abs(x0), np.abs(x1)) / scale > 1e12
    selected = np.flatnonzero(
        distant
        & (x0 != x1)
        & (np.maximum(x0, x1) >= minimum)
        & (np.minimum(x0, x1) <= maximum)
    )
    if len(selected) == 0:
        return x0, x1, y0, y1
    from decimal import Decimal, localcontext

    x0, x1, y0, y1 = x0.copy(), x1.copy(), y0.copy(), y1.copy()
    with localcontext() as context:
        context.prec = 700
        for index in selected:
            a, b, c, d = [
                Decimal.from_float(float(values[index])) for values in (x0, x1, y0, y1)
            ]
            left = min(max(x0[index], minimum), maximum)
            right = min(max(x1[index], minimum), maximum)
            y0[index] = float(
                c + (d - c) * (Decimal.from_float(float(left)) - a) / (b - a)
            )
            y1[index] = float(
                c + (d - c) * (Decimal.from_float(float(right)) - a) / (b - a)
            )
            x0[index], x1[index] = left, right
    return x0, x1, y0, y1
