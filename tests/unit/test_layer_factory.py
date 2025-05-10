import numpy as np

from uniplot.layer_factory import render_points
from uniplot.options import Options, CharacterSet
from uniplot.color import Color


def test_ascii_characters_without_color():
    xs = [np.array([1, 2, 3])]
    ys = [np.array([2, 1, 4])]
    opts = Options(
        character_set=CharacterSet.ASCII, x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0
    )
    matrix = render_points(xs, ys, opts)
    assert "+" in matrix


def test_ascii_characters_with_terminal_color():
    xs = [np.array([1, 2, 3])]
    ys = [np.array([2, 1, 4])]
    opts = Options(
        character_set=CharacterSet.ASCII,
        x_min=0.0,
        x_max=5.0,
        y_min=0.0,
        y_max=5.0,
        color=[Color.from_terminal("red")],
    )
    matrix = render_points(xs, ys, opts)
    assert _wrap_in_red("+") in matrix


def test_ascii_characters_with_rgb_color():
    xs = [np.array([1, 2, 3])]
    ys = [np.array([2, 1, 4])]
    opts = Options(
        character_set=CharacterSet.ASCII,
        x_min=0.0,
        x_max=5.0,
        y_min=0.0,
        y_max=5.0,
        height=3,
        width=3,
        color=[Color.from_rgb(146, 255, 12)],
    )
    matrix = render_points(xs, ys, opts)
    assert _wrap_in_lime_green("+") in matrix


def test_block_characters_without_color():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0)
    matrix = render_points(xs, ys, opts)
    assert "▖" in matrix


def test_block_characters_with_color():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(
        x_min=0.0, x_max=5.0, y_min=0.0, y_max=5.0, color=[Color.from_terminal("red")]
    )
    matrix = render_points(xs, ys, opts)
    assert _wrap_in_red("▖") in matrix


def test_block_characters_where_the_top_layer_should_hide_the_lower_layer():
    pixel_width = 5.0 / 10
    second_pixel_coord = 1.5 * pixel_width
    xs = [np.array([0, second_pixel_coord]), np.array([0, 5])]
    ys = [np.array([second_pixel_coord, 0]), np.array([0, 5])]
    opts = Options(
        x_min=0.0,
        x_max=5.0,
        y_min=0.0,
        y_max=5.0,
        width=6,
        height=6,
        lines=[False, False],
        color=False,
    )
    matrix = render_points(xs, ys, opts)
    # Make sure that the result is the same as in `test_block_characters_without_color`,
    # because the second series overwrites the first one.
    assert "▖" in matrix


def test_braille_characters_without_color():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(
        x_min=0.0,
        x_max=5.0,
        y_min=0.0,
        y_max=5.0,
        width=3,
        height=3,
        character_set=CharacterSet.BRAILLE,
    )
    matrix = render_points(xs, ys, opts)
    assert "⡀" in matrix


def test_braille_characters_with_color():
    xs = [np.array([0, 5])]
    ys = [np.array([0, 5])]
    opts = Options(
        x_min=0.0,
        x_max=5.0,
        y_min=0.0,
        y_max=5.0,
        width=3,
        height=3,
        character_set=CharacterSet.BRAILLE,
        color=[Color.from_terminal("red")],
    )
    matrix = render_points(xs, ys, opts)
    print(matrix)
    assert _wrap_in_red("⡀") in matrix


###########
# private #
###########


def _wrap_in_red(char: str) -> str:
    return "\033[31m" + str(char) + "\033[0m"


def _wrap_in_lime_green(char: str) -> str:
    return "\033[38;2;146;255;12m" + str(char) + "\033[0m"
