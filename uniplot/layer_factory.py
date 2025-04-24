import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple

import uniplot.pixel_matrix as pixel_matrix
import uniplot.plot_elements as elements
import uniplot.character_sets as character_sets
from uniplot.conversions import COLOR_CODES, convert_matrix_to_rows_of_submatrices
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
    # Setup: determine submatrix size, encoder, and character list
    scale_w, scale_h, encoder, char_list = _set_up_submatrix_shape_and_encoders(options)
    full_width = scale_w * options.width
    full_height = scale_h * options.height

    # Render input points into a full pixel matrix
    px_matrix = np.zeros((full_height, full_width), dtype=int)
    for i, (x, y) in enumerate(zip(xs, ys)):
        px_matrix = pixel_matrix.render(
            xs=x,
            ys=y,
            x_min=options.x_min,
            x_max=options.x_max,
            y_min=options.y_min,
            y_max=options.y_max,
            width=full_width,
            height=full_height,
            lines=options.lines[i],
            pixels=px_matrix,
            layer=i + 1,
        )  # type: ignore

    # Initialize output character matrix
    char_matrix = _init_character_matrix(width=options.width, height=options.height)

    # Break down pixel matrix into submatrices per character cell
    submatrices = convert_matrix_to_rows_of_submatrices(
        px_matrix,
        width_submatrix=scale_w,
        height_submatrix=scale_h,
    )

    color_matrix = submatrices.max(axis=2) - 1  # For optional color use

    if not options.force_ascii:
        max_vals = submatrices.max(axis=2, keepdims=True)
        submatrices = ((submatrices == max_vals) & (max_vals > 0)).astype(int)

    # Encode submatrices into integer values representing character shapes
    int_matrix = (submatrices * encoder).sum(axis=2)
    mask_nonzero = int_matrix != 0

    # Character decoding and assignment
    decoder = np.array(char_list)
    decoder[..., 0] = ""  # Blank character for zero entries
    char_matrix[mask_nonzero] = decoder[int_matrix[mask_nonzero]]

    # Apply color if enabled
    if options.color:
        colors = (
            [COLOR_CODES[c] for c in options.color]
            if isinstance(options.color, list)
            else COLOR_CODES.values()
        )

        decoder_colored = np.array(
            [
                np.char.add(np.char.add(c, char_list), elements.COLOR_RESET_CODE)
                for c in colors
            ]
        )
        indices = (
            color_matrix[mask_nonzero] % len(colors),
            int_matrix[mask_nonzero],
        )
        decoder_colored[..., 0] = ""
        char_matrix[mask_nonzero] = decoder_colored[indices]

    return char_matrix


def print_raw_pixel_matrix(pixels: NDArray, verbose: bool = False) -> None:
    """
    Just print the pixels.

    Used for testing and debugging.
    """
    join_char = "," if verbose else ""
    for row in pixels:
        print("DEBUG: (" + join_char.join(list(row)) + ")")


###########
# private #
###########


def _init_character_matrix(width: int, height: int, value: str = "") -> NDArray:
    return np.full((height, width), fill_value=value, dtype="<U15")


def _set_up_submatrix_shape_and_encoders(
    options: Options,
) -> Tuple[int, int, NDArray, List[str]]:
    if options.force_ascii:
        return (1, 1, np.array([1], ndmin=3), [" "] + options.force_ascii_characters)
    if options.character_set == "braille":
        return (
            2,
            4,
            np.array([1, 2, 4, 8, 16, 32, 64, 128], ndmin=3),
            character_sets.BRAILLE_CHARACTER_SET,
        )
    return (2, 2, np.array([1, 2, 4, 8], ndmin=3), character_sets.UNICODE_CHARACTER_SET)
