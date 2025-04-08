import numpy as np

from uniplot.layer_factory import render_points
from uniplot.options import Options


def test_ascii_characters():
    xs = [np.array([1, 2, 3])]
    ys = [np.array([2, 1, 4])]
    opts = Options(force_ascii=True, x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0)
    matrix = render_points(xs, ys, opts)
    assert "+" in matrix


def test_block_characters():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0)
    matrix = render_points(xs, ys, opts)
    assert "▖" in matrix


def test_braille_characters():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0, character_set="braille")
    matrix = render_points(xs, ys, opts)
    assert "⡀" in matrix
