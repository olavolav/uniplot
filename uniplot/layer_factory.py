import numpy as np
from numpy.typing import NDArray
from typing import List

import uniplot.pixel_matrix as pixel_matrix
import uniplot.plot_elements as elements
from uniplot.options import Options
from uniplot.discretizer import discretize


Y_GRIDLINE_CHARACTERS = ["▔", "─", "▁"]


def blank_character_matrix(width: int, height: int) -> NDArray:
    """
    Initialize an empty character matrix as a NumPy array.
    """
    return _init_character_matrix(width, height, value=" ")


def render_horizontal_gridline(y: float, options: Options) -> NDArray:
    """
    Render the pixel matrix that only consists of a line where the `y` value is.

    Because a character is higher than wide, this is rendered with "super-resolution"
    Unicode characters.
    """
    pixels = _init_character_matrix(width=options.width, height=options.height)
    if y < options.y_min or y >= options.y_max:
        return pixels

    if options.force_ascii:
        y_index = (
            options.height
            - 1
            - discretize(
                x=y, x_min=options.y_min, x_max=options.y_max, steps=options.height
            )
        )
        pixels[y_index, :] = "─"
    else:
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


def render_vertical_gridline(x: float, options: Options) -> NDArray:
    """
    Render the pixel matrix that only consists of a line where the `x` value is.
    """
    pixels = _init_character_matrix(width=options.width, height=options.height)
    if float(x) < float(options.x_min) or float(x) >= float(options.x_max):
        return pixels

    x_index = discretize(
        x=x, x_min=options.x_min, x_max=options.x_max, steps=options.width
    )

    pixels[:, x_index] = "│"

    return pixels


def render_points(xs: List[NDArray], ys: List[NDArray], options: Options) -> NDArray:
    # Determine if we use Unicode super-resolution :-) or not
    scaling_factor_width: int = 1
    scaling_factor_height: int = 1
    if not options.force_ascii:
        scaling_factor_width = 2
        scaling_factor_height = 4 if options.character_set == "braille" else 2
    matrix: NDArray = np.array([])

    for i in range(len(ys)):
        next_matrix = (i + 1) * pixel_matrix.render(
            xs=xs[i],
            ys=ys[i],
            x_min=options.x_min,
            x_max=options.x_max,
            y_min=options.y_min,
            y_max=options.y_max,
            width=scaling_factor_width * options.width,
            height=scaling_factor_height * options.height,
            lines=options.lines[i],
        )
        if i == 0:
            matrix = next_matrix
        else:
            matrix = pixel_matrix.merge_on_top(
                low_layer=matrix,
                high_layer=next_matrix,
                width=scaling_factor_width * options.width,
                height=scaling_factor_height * options.height,
            )

    if options.force_ascii:
        pixels = _init_character_matrix(width=options.width, height=options.height)
        for row in range(options.height):
            for col in range(options.width):
                pixels[row, col] = elements.character_for_ascii_pixel(
                    matrix[row, col],
                    options.force_ascii_characters,
                    color_mode=options.color,
                )
    elif options.character_set == "braille":
        pixels = _init_character_matrix(width=options.width, height=options.height)
        for row in range(options.height):
            for col in range(options.width):
                pixels[row, col] = elements.character_for_2by4_pixels(
                    matrix[4 * row : 4 * row + 4, 2 * col : 2 * col + 2],
                    color_mode=options.color,
                )
    else:
        pixels = _init_character_matrix(width=options.width, height=options.height, value=" ")
        x, y = np.shape(matrix)
        non_zeros = np.argwhere(matrix.reshape(x//2,2,y//2,2).sum(axis=(1,3))!=0)
        for row,col in non_zeros:
            m = matrix[2 * row : 2 * row + 2, 2 * col : 2 * col + 2]
            pixels[row,col] = elements.character_for_2by2_pixels(m,
                color_mode=options.color,
            )

    return pixels


def print_raw_pixel_matrix(pixels: NDArray, verbose: bool = False) -> None:
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


def _init_character_matrix(width: int, height: int, value: str = "") -> NDArray:
    return np.full((height, width), fill_value=value, dtype="<U15")
