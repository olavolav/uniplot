import numpy as np  # type: ignore
from typing import List

import uniplot.pixel_matrix
import uniplot.plot_elements as elements
from uniplot.options import Options


def merge_layers(character_layers: List[np.array], options: Options) -> np.array:
    # Initialize with blank layer consisting of spaces only
    merged_layer = _blank_pixel_character_matrix(
        width=options.width, height=options.height
    )

    # Merge layers on top
    for character_layer in character_layers:
        # Just checking
        assert character_layer.shape == (options.height, options.width)
        for row_index in range(options.height):
            for column_index in range(options.width):
                if character_layer[row_index, column_index] != "":
                    merged_layer[row_index, column_index] = character_layer[
                        row_index, column_index
                    ]

    return merged_layer


def render_y_gridline(y: float, options: Options) -> np.array:
    """
    Render the pixel matrix that only consists of a dashed line where the `y` value is.
    """
    pixels = _init_pixel_character_matrix(width=options.width, height=options.height)
    if y < options.y_min or y >= options.y_max:
        return pixels

    y_index = _discretize_number(
        x=y, x_min=options.y_min, x_max=options.y_max, steps=options.height
    )
    pixels[options.height - 1 - y_index, :] = "-"

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


def _blank_pixel_character_matrix(width: int, height: int) -> np.array:
    return _init_pixel_character_matrix(width, height, value=" ")


def _discretize_number(x: float, x_min: float, x_max: float, steps: int) -> int:
    """
    Returns a discretized integer.
    """
    return int(((x - x_min) / (x_max - x_min)) * steps)
