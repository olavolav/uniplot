import sys
import numpy as np  # type: ignore
from typing import List, Optional

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
    ticks = [
        _compute_y_at_middle_of_row(i, y_min=y_min, y_max=y_max, height=height)
        if ((i % 4 == 0 and i != height - 2) or i == height - 1)
        else None
        for i in range(height)
    ]

    return _find_shortest_string_representation(ticks)


def xaxis_ticks(x_min: float, x_max: float, width: int) -> str:
    """
    This will generate the x axis ticks marks.

    It returns a string.
    """
    # TODO For now let's just render min and max at appropriate positions.
    min_str, max_str = _find_shortest_string_representation([x_min, x_max])
    buffer = int(round(width - len(min_str) - 0.5 * len(max_str) - 1))
    if buffer > 1:
        return f" {min_str}{' '*buffer}{max_str}"
    return f" {min_str} up to {max_str}"


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


def _find_shortest_string_representation(numbers: List[Optional[float]],) -> List[str]:
    """
    This method will find the shortest numerical values for axis labels that are different from ech other.
    """
    # We actually want to add one more digit than needed for uniqueness
    return_next = False
    for nr_digits in range(10):
        test_list = ["" if n is None else _float_format(n, nr_digits) for n in numbers]
        if return_next:
            return test_list
        compact_list = [n for n in test_list if n != ""]
        if len(compact_list) == len(set(compact_list)):
            return_next = True

    # Fallback to naive string conversion
    return ["" if n is None else str(n) for n in numbers]


def _float_format(n: float, nr_digits: int):
    return ("{:,." + str(nr_digits) + "f}").format(float(n))
