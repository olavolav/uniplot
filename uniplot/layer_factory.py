import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple

import uniplot.pixel_matrix as pixel_matrix
import uniplot.plot_elements as elements
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
    # Determine scaling factors and resultion of the dor matrix underlying the characters
    # scaling_factor_width: int = 1
    # scaling_factor_height: int = 1
    # if not options.force_ascii:
    #     scaling_factor_width = 2
    #     scaling_factor_height = 4 if options.character_set == "braille" else 2
    (scaling_factor_width, scaling_factor_height, encoder) = _set_up_submatrix_shape_and_encoders(options)
    height, width = (
        scaling_factor_height * options.height,
        scaling_factor_width * options.width,
    )

    # Render the `xs` and `ys` into a dot matrix
    px_matrix: NDArray = np.zeros((height, width), dtype=int)
    for i in range(len(ys)):
        px_matrix = pixel_matrix.render(
            xs=xs[i],
            ys=ys[i],
            x_min=options.x_min,
            x_max=options.x_max,
            y_min=options.y_min,
            y_max=options.y_max,
            width=width,
            height=height,
            lines=options.lines[i],
            pixels=px_matrix,
            layer=i + 1,
        )

    # Render the dot matrix into characters
    char_matrix = _init_character_matrix(width=options.width, height=options.height)
    submatrices = convert_matrix_to_rows_of_submatrices(px_matrix, width_submatrix=scaling_factor_width, height_submatrix=scaling_factor_height)
    if options.color:
        # color = submatrices.max(axis=(2)) - 1  # check color
        submatrices = np.clip(submatrices, a_min=0, a_max=1)  # type: ignore
    # Encode
    new_pix = (submatrices * encoder).sum(axis=(2))
    non_zero_mask = new_pix != 0

    decoder_c = np.array(elements.UNICODE_SQUARES)
    index = new_pix[non_zero_mask]

    decoder_c[..., 0] = ""
    char_matrix[non_zero_mask] = decoder_c[index]

    # if options.force_ascii:
    #     # If using ASCII characters
    #     for row in range(options.height):
    #         for col in range(options.width):
    #             char_matrix[row, col] = elements.character_for_ascii_pixel(
    #                 px_matrix[row, col],
    #                 options.force_ascii_characters,
    #                 color_mode=options.color,
    #             )
    # elif options.character_set == "braille":
    #     # If using Braille characters
    #     for row in range(options.height):
    #         for col in range(options.width):
    #             char_matrix[row, col] = elements.character_for_2by4_pixels(
    #                 px_matrix[4 * row : 4 * row + 4, 2 * col : 2 * col + 2],
    #                 color_mode=options.color,
    #             )
    # else:
    #     # If using Box characters
    #     color = None
    #     # Used to be character_for_2by2_pixels
    #     # TODO Use such a logic also for the other character sets
    #     encoder = np.array([1, 2, 4, 8], ndmin=3)
    #     mat = np.swapaxes(
    #         px_matrix.reshape(height // 2, 2, width // 2, 2), 1, 2
    #     ).reshape((height // 2, width // 2, 4))
    #     if options.color:
    #         color = mat.max(axis=(2)) - 1  # check color
    #         mat = np.clip(mat, a_min=0, a_max=1)  # type: ignore
    #     new_pix = (mat * encoder).sum(axis=(2))  # decoder
    #     non_zero_mask = new_pix != 0

    #     if options.color:
    #         assert color is not None
    #         colors = (
    #             [COLOR_CODES[c] for c in options.color]
    #             if isinstance(options.color, list)
    #             else COLOR_CODES.values()
    #         )
    #         decoder_c = np.array(
    #             [
    #                 np.char.add(
    #                     np.char.add(c, elements.UNICODE_SQUARES),
    #                     elements.COLOR_RESET_CODE,
    #                 )
    #                 for c in colors
    #             ]
    #         )
    #         index = color[non_zero_mask] % len(colors), new_pix[non_zero_mask]
    #     else:
    #         decoder_c = np.array(elements.UNICODE_SQUARES)
    #         index = new_pix[non_zero_mask]
    #     decoder_c[..., 0] = ""
    #     char_matrix[non_zero_mask] = decoder_c[index]
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


def _set_up_submatrix_shape_and_encoders(options: Options) -> Tuple[int, int, NDArray]:
    if options.force_ascii:
        return (1,1,np.array([1], ndmin=3))
    if options.character_set == "braille":
        return (2,4,np.array([1,2,4,8,16,32,64,128], ndmin=3))
    return (2,2,np.array([1,2,4,8], ndmin=3))