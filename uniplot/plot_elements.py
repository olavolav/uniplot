import sys
import re
import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple, Union, Optional, Final

from uniplot.conversions import COLOR_CODES
from functools import wraps

UNICODE_SQUARES: Final = [
    "",
    "▘",
    "▝",
    "▀",
    "▖",
    "▌",
    "▞",
    "▛",
    "▗",
    "▚",
    "▐",
    "▜",
    "▄",
    "▙",
    "▟",
    "█",
]

BINARY_ENCODING_MATRIX: Final = np.array([[1, 2], [4, 8]])
BINARY_ENCODING_MATRIX_BRAILLE_BYTE2: Final = np.array(
    [
        [0, 0],
        [0, 0],
        [0, 0],
        [1, 2],
    ]
)
BINARY_ENCODING_MATRIX_BRAILLE_BYTE3: Final = np.array(
    [
        [1, 8],
        [2, 16],
        [4, 32],
        [0, 0],
    ]
)

CURSOR_UP_ONE: Final = "\x1b[1A"
ERASE_LINE: Final = "\x1b[2K"

DEFAULT_COLORS: Final = list(COLOR_CODES.values())

COLOR_RESET_CODE: Final = "\033[0m"
COLOR_CODE_REGEX: Final = re.compile(r"\033\[\d+m")


def np_cache(func):
    """A simple cache decorator that uses hashable keys for NumPy arrays."""
    cache = {}

    @wraps(func)
    def wrapper(arr, **kwargs):
        key = arr.data.tobytes()  # hashable version
        if key not in cache:
            cache[key] = func(arr, **kwargs)
        return cache[key]

    return wrapper


@np_cache
def character_for_2by4_pixels(
    square: NDArray, color_mode: Union[bool, List[str]] = False
) -> str:
    """
    Convert width 2 x height 4 matrix (non-negative integers) to unicode Braille character
    representation for plotting.
    """
    assert square.shape == (4, 2)
    assert square.min() >= 0

    # Postprocess to remove everything that is not max color
    max_color = square.max()
    if max_color <= 1:
        binary_square = np.clip(square, a_min=0, a_max=1)
    else:
        binary_square = np.clip(square, a_min=max_color - 1, a_max=max_color) - (
            max_color - 1
        )

    bstr = bytes("⠀", "utf-8")
    byte2 = (
        np.multiply(binary_square, BINARY_ENCODING_MATRIX_BRAILLE_BYTE2)
        .sum()
        .astype(int)
    )
    byte3 = (
        np.multiply(binary_square, BINARY_ENCODING_MATRIX_BRAILLE_BYTE3)
        .sum()
        .astype(int)
    )
    char = bytes([bstr[0], bstr[1] + byte2, bstr[2] + byte3]).decode("utf-8")

    # Reset to no character to make layers opaque
    if byte2 == 0 and byte3 == 0:
        char = ""

    return _colorize_char(char, max_color, color_mode)


def character_for_ascii_pixel(
    nr: int,
    force_ascii_characters: List[str],
    color_mode: Union[bool, List[str]] = False,
) -> str:
    # NOTE We assume that this function is only being called when the
    # `force_ascii` option is enabled.
    if nr < 1:
        return ""
    return force_ascii_characters[(nr - 1) % len(force_ascii_characters)]


def legend(
    legend_labels: List[str],
    width: int,
    line_length_hard_cap: Optional[int],
    color: Union[bool, List[str]],
    force_ascii: bool = False,
    force_ascii_characters: List[str] = [],
    character_set: str = "box",
) -> str:
    """
    Assemble a legend that shows the color of the different curves.
    """
    label_strings: List[str] = []
    for i, legend in enumerate(legend_labels):
        symbol: str = "█"
        if force_ascii:
            symbol = force_ascii_characters[i % len(force_ascii_characters)]
        elif character_set == "braille":
            symbol = "⣿"

        label_string = (
            _colorize_char(symbol * 2, i + 1, color) + " " + str(legend).strip()
        )
        label_strings.append(label_string)

    full_label_string = "\n".join(label_strings)

    return _center_if_possible(full_label_string, width + 2, line_length_hard_cap)


def plot_title(title: str, width: int, line_length_hard_cap: Optional[int]) -> str:
    """
    Returns the centered title string.

    Note that this assumes that `title` is not `None`.
    """
    return _center_if_possible(title, width + 2, line_length_hard_cap)


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


def count_lines(text: str) -> int:
    """
    Returns the number of lines that `print(text)` will produce. Note that
    passing None or an empty string will yield `1`, because that is how the
    `print` function works in Python.
    """
    return text.__str__().count("\n") + 1


###########
# private #
###########


def _center_if_possible(
    text: str, width: int, line_length_hard_cap: Optional[int]
) -> str:
    """
    This centers the input `text` by adding left padding if the width of all
    lines of `text` is smaller than width. Otherwise, it simply returns the
    input text and relies on the console line break.
    """
    lines = text.splitlines()
    max_len = max([len(_text_without_control_chars(line)) for line in lines])

    effective_width = (
        width if line_length_hard_cap is None else min(width, line_length_hard_cap)
    )
    if max_len >= effective_width:
        return text

    # Apply padding on the left of each line
    offset = int((effective_width - max_len) / 2)
    return "\n".join([" " * offset + line for line in lines])


def _text_without_control_chars(text: str):
    return COLOR_CODE_REGEX.sub("", text)


def _colorize_char(char: str, color_nr: int, color_mode: Union[bool, List[str]]) -> str:
    if char == "" or color_mode is False or color_nr < 1:
        return char
    colors = (
        _colors_to_codes(color_mode) if isinstance(color_mode, list) else DEFAULT_COLORS
    )
    color_code = colors[(color_nr - 1) % len(colors)]
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
