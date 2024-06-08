import sys
import re
import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple, Optional

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
DEFAULT_COLORS = list(COLOR_CODES.values())

COLOR_RESET_CODE = "\033[0m"
COLOR_CODE_REGEX = re.compile(r"\033\[\d+m")


def character_for_2by2_pixels(
    square: NDArray, color_mode: bool | Optional[List[str]] = False
) -> str:
    """
    Convert 2x2 matrix (non-negative integers) to unicode character
    representation for plotting.
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

    integer_encoding = np.multiply(binary_square, BINARY_ENCODING_MATRIX).sum()
    char = UNICODE_SQUARES[integer_encoding]

    # We are done if the result is a blank character, or if the result is not
    # blank and we do not need to colorize it
    if char == "" or not color_mode:
        return char
    return _colorize_char(char, square.max(), color_mode)


def character_for_ascii_pixel(
    nr: int, color_mode: bool | Optional[List[str]] = False
) -> str:
    if nr < 1:
        return ""
    if not color_mode:
        return "█"
    return _colorize_char("█", nr, color_mode)


def legend(
    legend_labels: List[str], width: int, colors: Optional[List[str]] = None
) -> str:
    """
    Assemble a legend that shows the color of the different curves.
    """
    color = _colors_to_codes(colors) if isinstance(colors, list) else DEFAULT_COLORS

    label_strings: List[str] = []
    for i, legend in enumerate(legend_labels):
        label_string = (
            f"{color[i % len(color)]}██{COLOR_RESET_CODE} {str(legend).strip()}"
        )
        label_strings.append(label_string)

    full_label_string = "\n".join(label_strings)

    return _center_if_possible(full_label_string, width=width + 2)


def plot_title(title: str, width: int) -> str:
    """
    Returns the centered title string.

    Note that this assumes that `title` is not `None`.
    """
    return _center_if_possible(title, width=width + 2)


def erase_previous_lines(nr_lines: int) -> None:
    """
    This used terminal codes to erase the last `nr_lines` lines.
    """
    for _ in range(nr_lines):
        sys.stdout.write(ERASE_LINE)
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def compute_bar_chart_histogram_points(
    values: NDArray, bin_edges: List[float]
) -> Tuple:
    """
    Given an input Numpy array `values`, this computes the histogram according
    to the provided `bin_edges` and returns the points that form a bar chart
    when plotted.

    Returns a tuple of two NumPy arrays, which are the x and y coordinates of
    the points of the bar chart.
    """
    counts, _ = np.histogram(values, bins=bin_edges)
    return _histogram_to_bar_chart_points(bin_edges, counts)


###########
# private #
###########


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


def _colorize_char(char: str, color: int, colors: Optional[List[str]] = None) -> str:
    colors = _colors_to_codes(colors) if isinstance(colors, list) else DEFAULT_COLORS
    color_code = colors[(color - 1) % len(colors)]
    return color_code + char + COLOR_RESET_CODE


def _colors_to_codes(colors: List[str]):
    return [COLOR_CODES.get(i, " ") for i in colors]


def _histogram_to_bar_chart_points(bin_edges, counts) -> Tuple:
    bins = len(bin_edges) - 1
    # Draw vertical and horizontal lines to connect points
    xs_here = np.zeros(1 + 2 * bins + 1)
    ys_here = np.zeros(1 + 2 * bins + 1)
    xs_here[0] = bin_edges[0]
    xs_here[1::2] = bin_edges
    xs_here[2::2] = bin_edges[1:]
    ys_here[1:-1:2] = counts
    ys_here[2:-1:2] = counts
    return (xs_here, ys_here)
