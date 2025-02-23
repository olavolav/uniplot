import numpy as np
from numpy.typing import NDArray
from typing import List

import uniplot.pixel_matrix as pixel_matrix
import uniplot.plot_elements as elements
from uniplot.conversions import COLOR_CODES
from uniplot.options import Options
from uniplot.discretizer import discretize


Y_GRIDLINE_CHARACTERS = ["▔", "─", "▁"]
ad, squares, resets = np.char.add, elements.UNICODE_SQUARES, elements.COLOR_RESET_CODE


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

    # ideally we 1 create empty on

    height, width = (
        scaling_factor_width * options.height,
        scaling_factor_height * options.width,
    )
    matrix: NDArray = np.zeros((height, width), dtype=int)

    for i in range(len(ys)):
        # I think this overrides not sum so we can avoid posprocess if layers are 2**x
        matrix = pixel_matrix.render(
            xs=xs[i],
            ys=ys[i],
            x_min=options.x_min,
            x_max=options.x_max,
            y_min=options.y_min,
            y_max=options.y_max,
            width=width,
            height=height,
            lines=options.lines[i],
            pixels=matrix,
            layer=i + 1,
        )

    pixels = _init_character_matrix(width=options.width, height=options.height)
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
        color = None
        # Used to be character_for_2by2_pixels
        encoder2 = np.array([1, 2, 4, 8], ndmin=3)
        mat = np.swapaxes(matrix.reshape(height // 2, 2, width // 2, 2), 1, 2).reshape(
            (height // 2, width // 2, 4)
        )
        if options.color:
            color = mat.max(axis=(2)) - 1  # check color
            mat = np.clip(mat, a_min=0, a_max=1)  # to black and white
        new_pix = (mat * encoder2).sum(axis=(2))  # decoder
        non_zero_mask = new_pix != 0

        if options.color:
            assert color is not None
            colors = (
                [COLOR_CODES[c] for c in options.color]
                if isinstance(options.color, list)
                else COLOR_CODES.values()
            )
            decoder_c = np.array([ad(ad(c, squares), resets) for c in colors])
            index = color[non_zero_mask], new_pix[non_zero_mask]
        else:
            decoder_c = np.array(squares)
            index = new_pix[non_zero_mask]
        decoder_c[..., 0] = ""
        pixels[non_zero_mask] = decoder_c[index]
        # pixels=decoder_c[new_pix] #also ok, no needs pixels defined
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
