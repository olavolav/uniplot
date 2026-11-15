"""Fill coverage checked against small polygons, independently of rasterization."""

import importlib

import numpy as np
import pytest

from uniplot import pixel_matrix


def render(xs, ys, fill=0, width=3, height=3, **kwargs):
    return pixel_matrix.render(
        np.asarray(xs, dtype=float),
        np.asarray(ys, dtype=float),
        x_min=0,
        x_max=2,
        y_min=0,
        y_max=2,
        width=width,
        height=height,
        fill=fill,
        **kwargs,
    )


@pytest.fixture(params=["numpy", "numba"])
def backend(request, monkeypatch):
    module = importlib.import_module("uniplot.fill")
    if request.param == "numba":
        if module._render_numba is None:
            pytest.skip("Numba is unavailable")
        monkeypatch.setattr(module, "_render", module._render_numba)
    else:
        monkeypatch.setattr(module, "_render", module._render_numpy)


def test_triangle_and_reversal(backend):
    expected = [[0, 0, 1], [0, 1, 1], [1, 1, 1]]
    np.testing.assert_array_equal(render([0, 2], [0, 2]), expected)
    np.testing.assert_array_equal(render([2, 0], [2, 0]), expected)


@pytest.mark.parametrize(
    "ys, baseline, expected",
    [
        ([3, 3], 0, [[1] * 3] * 3),
        ([3, 3], 4, [[0] * 3] * 3),
        ([-1, -1], 1, [[0] * 3, [1] * 3, [1] * 3]),
        ([-1, -1], -2, [[0] * 3] * 3),
    ],
)
def test_offscreen_boundary(backend, ys, baseline, expected):
    np.testing.assert_array_equal(render([-1, 3], ys, fill=baseline), expected)


def test_isolated_points_and_zero_area(backend):
    for xs, ys, baseline in [
        ([1], [1], 0),
        ([0, 2], [1, 1], 1),
        ([1, 1], [0, 2], 0),
    ]:
        np.testing.assert_array_equal(
            render(xs, ys, fill=baseline), render(xs, ys, fill=None)
        )


def test_tiny_area_survives(backend):
    # Both points occupy the top row; only fill can paint the rows below.
    pixels = render([0.7, 0.8], [1.9, 1.9])
    np.testing.assert_array_equal(pixels, [[0, 1, 0]] * 3)


def test_extreme_offscreen_coordinates(backend):
    np.testing.assert_array_equal(
        render([-1e300, 1e300], [1e300, 1e300]), np.ones((3, 3))
    )


def test_batch_boundaries_and_retracing(backend):
    xs, ys = [0, 2, 0, 2], [2, 2, 1, 1]
    np.testing.assert_array_equal(render(xs, ys, batch_size=1), np.ones((3, 3)))


def clip_polygon(points, axis, edge, keep_above):
    result = []
    for previous, current in zip(points[-1:] + points[:-1], points):
        previous_inside = (
            (previous[axis] >= edge) if keep_above else (previous[axis] <= edge)
        )
        current_inside = (
            (current[axis] >= edge) if keep_above else (current[axis] <= edge)
        )
        if previous_inside != current_inside:
            t = (edge - previous[axis]) / (current[axis] - previous[axis])
            result.append(tuple(a + t * (b - a) for a, b in zip(previous, current)))
        if current_inside:
            result.append(current)
    return result


def reference(xs, ys, baseline, width, height):
    pixels = render(xs, ys, fill=None, width=width, height=height)
    x_edges = np.r_[0, (np.arange(width - 1) + 0.5) * 2 / max(1, width - 1), 2]
    y_edges = np.r_[0, (np.arange(height - 1) + 0.5) * 2 / max(1, height - 1), 2]
    for x0, x1, y0, y1 in zip(xs[:-1], xs[1:], ys[:-1], ys[1:]):
        if not np.all(np.isfinite([x0, x1, y0, y1])):
            continue
        # Split a crossing before constructing a simple polygon.
        segments = [(x0, x1, y0, y1)]
        if (y0 - baseline) * (y1 - baseline) < 0:
            cross = x0 + (baseline - y0) / (y1 - y0) * (x1 - x0)
            segments = [(x0, cross, y0, baseline), (cross, x1, baseline, y1)]
        for a, b, c, d in segments:
            for row in range(height):
                for col in range(width):
                    polygon = [(a, baseline), (a, c), (b, d), (b, baseline)]
                    for axis, edge, above in [
                        (0, x_edges[col], True),
                        (0, x_edges[col + 1], False),
                        (1, y_edges[row], True),
                        (1, y_edges[row + 1], False),
                    ]:
                        polygon = clip_polygon(polygon, axis, edge, above)
                    area = abs(
                        sum(
                            p[0] * q[1] - q[0] * p[1]
                            for p, q in zip(polygon, polygon[1:] + polygon[:1])
                        )
                    )
                    if area > 1e-12:
                        pixels[height - 1 - row, col] = 1
    return pixels


def test_random_geometry_against_polygon_reference(backend):
    rng = np.random.default_rng(42)
    for _ in range(30):
        xs, ys = rng.uniform(-2, 4, (2, 8))
        baseline = rng.uniform(-2, 4)
        np.testing.assert_array_equal(
            render(xs, ys, fill=baseline, width=5, height=4),
            reference(xs, ys, baseline, 5, 4),
        )


def test_filled_line_stroke_matches_existing_sampling():
    # Compare strokes directly so the filled area cannot hide missing line pixels.
    rng = np.random.default_rng(8)
    for _ in range(30):
        xs, ys = rng.uniform(-4, 6, (2, 8))
        options = {
            "xs": xs,
            "ys": ys,
            "x_min": 0,
            "x_max": 2,
            "y_min": 0,
            "y_max": 2,
            "width": 3,
            "height": 3,
        }
        expected = pixel_matrix._render_batch_of_lines(**options)
        actual = pixel_matrix._render_bounded_lines(
            **options, pixels=np.zeros((3, 3), dtype=np.int32)
        )
        np.testing.assert_array_equal(actual, expected)


def test_nonfinite_samples_break_connections(backend):
    for missing in [np.nan, np.inf, -np.inf]:
        pixels = render([0, 1, 2], [1, missing, 1], lines=True)
        np.testing.assert_array_equal(pixels, render([0, 2], [1, 1], fill=None))


@pytest.mark.parametrize("lines", [False, True])
def test_single_cell_does_not_show_wholly_offscreen_geometry(backend, lines):
    pixels = render([0, 2], [3, 3], fill=4, width=1, height=1, lines=lines)
    np.testing.assert_array_equal(pixels, [[0]])


@pytest.mark.parametrize(
    "xs,ys,baseline,width,height",
    [
        pytest.param([-3, -1], [1, 2], 0, 5, 4, id="left-of-view"),
        pytest.param([3, 4], [1, 2], 0, 5, 4, id="right-of-view"),
        pytest.param([0, 2], [-1, 3], 1, 5, 4, id="baseline-crossing"),
        pytest.param([0, 2], [0.5, 0.5], 0, 5, 4, id="cell-edge"),
        pytest.param([0, 1, 1, 2], [0, 2, 0, 2], 0, 5, 4, id="vertical-segment"),
        pytest.param([0, 2], [-1, 3], 1, 1, 1, id="single-cell"),
        pytest.param([0, 2], [-1, 3], 1, 1, 4, id="single-column"),
        pytest.param([0, 2], [-1, 3], 1, 5, 1, id="single-row"),
    ],
)
def test_clipping_and_cell_edges_against_reference(
    backend, xs, ys, baseline, width, height
):
    np.testing.assert_array_equal(
        render(xs, ys, fill=baseline, width=width, height=height),
        reference(xs, ys, baseline, width, height),
    )


def test_gap_at_batch_boundary(backend):
    xs, ys = [0, 0.5, 1, 1.5, 2], [1, 1, np.nan, 2, 2]
    expected = reference(xs, ys, 0, 5, 4)
    for batch_size in [2, 3]:
        np.testing.assert_array_equal(
            render(xs, ys, width=5, height=4, batch_size=batch_size), expected
        )


@pytest.mark.parametrize("lines", [False, True])
def test_extreme_diagonal_preserves_visible_slope(backend, lines):
    np.testing.assert_array_equal(
        render([-1e100, 1e100], [-1e100, 1e100], lines=lines),
        render([0, 2], [0, 2], lines=lines),
    )


def test_fill_is_invariant_under_x_translation(backend):
    offset = 1e9
    actual = pixel_matrix.render(
        np.array([offset, offset + 2]),
        np.array([0.0, 2.0]),
        offset,
        offset + 2,
        0,
        2,
        5,
        5,
        fill=0,
    )
    np.testing.assert_array_equal(actual, render([0, 2], [0, 2], width=5, height=5))
