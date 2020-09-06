import sys
import re
import numpy as np  # type: ignore
from typing import List, Optional

from uniplot.discretizer import compute_y_at_middle_of_row

UNICODE_SQUARES = {
    0: "",
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

COLOR_CODES = {
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "red": "\033[31m",
}
COLOR_RESET_CODE = "\033[0m"
COLOR_CODE_REGEX = re.compile(r"\033\[\d+m")


def character_for_2by2_pixels(square: np.array, color_mode: bool = False) -> str:
    """
    Convert 2x2 matrix (non-negative integers) to unicode character representation for plotting.
    """
    assert square.shape == (2, 2)
    assert square.min() >= 0

    # Postprocess to remove everything that is not max color
    max_color = square.max()
    if max_color <= 1:
        binary_square = np.clip(square, a_min=0, a_max=1)
    else:
        binary_square = np.clip(square, a_min=max_color - 1, a_max=max_color) - (
            max_color - 1
        )

    # binary_square = np.clip(square, a_min=0, a_max=1)
    integer_encoding = np.multiply(binary_square, BINARY_ENCODING_MATRIX).sum()
    char = UNICODE_SQUARES[integer_encoding]

    if char == "" or not color_mode:
        return char

    color_code = list(COLOR_CODES.values())[(square.max() - 1) % len(COLOR_CODES)]
    return f"{color_code}{char}{COLOR_RESET_CODE}"


def legend(legend_labels: List[str], width: int) -> str:
    """
    Assemble a legend that shows the color of the different curves.
    """
    label_strings: List[str] = []

    for i in range(len(legend_labels)):
        color_code = list(COLOR_CODES.values())[i % len(COLOR_CODES)]
        label_string = (
            f"{color_code}██{COLOR_RESET_CODE} {str(legend_labels[i]).strip()}"
        )
        label_strings.append(label_string)

    full_label_string = "\n".join(label_strings)

    return _center_if_possible(full_label_string, width=width + 2)


def yaxis_ticks(y_min: float, y_max: float, height: int) -> List[str]:
    """
    This will generate the y axis ticks marks.

    It returns an array of length `height`.
    """
    ticks = [
        compute_y_at_middle_of_row(
            height_index_from_top=i, y_min=y_min, y_max=y_max, height=height
        )
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


def plot_title(title: str, width: int) -> str:
    """
    Returns the centered title string.

    Note that this assumes that `title` is not `None`.
    """
    return _center_if_possible(title, width=width + 2)


def erase_previous_lines(nr_lines: int) -> None:
    for i in range(nr_lines):
        sys.stdout.write(ERASE_LINE)
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


###########
# private #
###########


def _find_shortest_string_representation(numbers: List[Optional[float]]) -> List[str]:
    """
    This method will find the shortest numerical values for axis labels that are different from ech other.
    """
    # We actually want to add one more digit than needed for uniqueness
    for nr_digits in range(10):
        test_list = ["" if n is None else _float_format(n, nr_digits) for n in numbers]
        compact_list = [n for n in test_list if n != ""]
        if len(compact_list) == len(set(compact_list)):
            return test_list

    # Fallback to naive string conversion
    return ["" if n is None else str(n) for n in numbers]


def _float_format(n: float, nr_digits: int):
    if nr_digits == 0:
        return ("{:,d}").format(int(n))
    return ("{:,." + str(nr_digits) + "f}").format(float(n))


def _center_if_possible(text: str, width: int) -> str:
    lines = text.splitlines()
    max_len = max([len(_text_without_control_chars(line)) for line in lines])

    if max_len >= width:
        return text

    # Apply padding on the left of each line
    offset = int((width - max_len) / 2)
    return "\n".join([" " * offset + line for line in lines])


def _text_without_control_chars(text: str):
    return COLOR_CODE_REGEX.sub("", text)
