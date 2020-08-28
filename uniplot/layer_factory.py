import numpy as np  # type: ignore
from typing import List

import uniplot.pixel_matrix
import uniplot.plot_elements as elements
from uniplot.options import Options
from uniplot.discretizer import discretize


Y_GRIDLINE_CHARACTERS = ["▔", "─", "▁"]


def blank_pixel_character_matrix(width: int, height: int) -> np.array:
    """
    Initialize an empty character matrix as a NumPy array.
    """
    return _init_pixel_character_matrix(width, height, value=" ")


def render_horizontal_gridline(y: float, options: Options) -> np.array:
    """
    Render the pixel matrix that only consists of a line where the `y` value is.

    Because a character is higher than wide, this is rendered with "super-resolution"
    Unicode characters.
    """
    pixels = _init_pixel_character_matrix(width=options.width, height=options.height)
    if y < options.y_min or y >= options.y_max:
        return pixels

    y_index_superresolution = (
        3 * options.height
        - 1
        - discretize(
            x=y, x_min=options.y_min, x_max=options.y_max, steps=3 * options.height
        )
    )
    y_index = int(y_index_superresolution / 3)

    character = Y_GRIDLINE_CHARACTERS[y_index_superresolution % 3]
    pixels[y_index, :] = character

    return pixels


def render_vertical_gridline(x: float, options: Options) -> np.array:
    """
    Render the pixel matrix that only consists of a line where the `x` value is.
    """
    pixels = _init_pixel_character_matrix(width=options.width, height=options.height)
    if x < options.x_min or x >= options.x_max:
        return pixels

    x_index = discretize(
        x=x, x_min=options.x_min, x_max=options.x_max, steps=options.width
    )

    pixels[:, x_index] = "│"

    return pixels


def render_points(xs: np.array, ys: np.array, options: Options) -> np.array:
    matrix = uniplot.pixel_matrix.render(
        xs=xs,
        ys=ys,
        x_min=options.x_min,
        x_max=options.x_max,
        y_min=options.y_min,
        y_max=options.y_max,
        # Unicode super-resolution :-)
        width=2 * options.width,
        height=2 * options.height,
    )

    pixels = _init_pixel_character_matrix(width=options.width, height=options.height)
    for row in range(options.height):
        for col in range(options.width):
            pixels[row, col] = elements.character_for_2by2_pixels(
                matrix[2 * row : 2 * row + 2, 2 * col : 2 * col + 2]
            )

    return pixels


def print_raw_pixel_matrix(pixels: np.array, verbose: bool = False) -> None:
    """
    Just print the pixels.

    This is mostly used for testing and debugging.
    """
    join_char = "," if verbose else ""
    for row in pixels:
        print("DEBUG: (" + join_char.join(list(row)) + ")")


###########
# private #
###########


def _init_pixel_character_matrix(width: int, height: int, value: str = "") -> np.array:
    return np.full((height, width), fill_value=value)
