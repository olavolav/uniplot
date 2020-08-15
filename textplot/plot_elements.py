import sys
import numpy as np  # type: ignore
from typing import List

UNICODE_SQUARES = {
    0: " ",
    1: "▘",
    2: "▝",
    3: "▀",
    4: "▖",
    5: "▌",
    6: "▞",
    7: "▛",
    8: "▗",
    9: "▚",
    10: "▐",
    11: "▜",
    12: "▄",
    13: "▙",
    14: "▟",
    15: "█",
}
BINARY_ENCODING_MATRIX = np.array([[1, 2], [4, 8]])

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"


def character_for_2by2_pixels(square: np.array) -> str:
    """
    Convert 2x2 matrix to unicode character representation for plotting.
    """
    # Convert matric to integer
    # NOTE That this will fail if the square is not 2x2 or contains anything else than
    # zeros and ones
    integer_encoding = np.multiply(square, BINARY_ENCODING_MATRIX).sum()
    return UNICODE_SQUARES[integer_encoding]


def yaxis_ticks(y_min: float, y_max: float, height: int) -> List[str]:
    """
    This will generate the y axis ticks marks.

    It returns an array of length `height`.
    """
    return [
        str(_compute_y_at_middle_of_row(i, y_min=y_min, y_max=y_max, height=height))
        if ((i % 4 == 0 and i != height - 2) or i == height - 1)
        else ""
        for i in range(height)
    ]


def xaxis_ticks(x_min: float, x_max: float, width: int) -> str:
    """
    This will generate the x axis ticks marks.

    It returns a string.
    """
    # TODO For now let's just render min and max at appropriate positions.
    buffer = int(round(width - len(str(x_min)) - 0.5 * len(str(x_max))) - 1)
    if buffer > 1:
        return f" {x_min}{' '*buffer}{x_max}"
    return f" {x_min} up to {x_max}"


def erase_previous_lines(nr_lines: int) -> None:
    for i in range(nr_lines):
        sys.stdout.write(ERASE_LINE)
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


###########
# private #
###########


def _compute_y_at_middle_of_row(
    height_index_from_top: int, y_min: float, y_max: float, height: int
) -> float:
    return ((y_max - y_min) / height) * (height - height_index_from_top + 0.5) + y_min
