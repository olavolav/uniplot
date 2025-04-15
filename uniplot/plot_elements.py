import sys
import re
import numpy as np
from numpy.typing import NDArray
from typing import List, Tuple, Union, Optional, Final

from uniplot.conversions import COLOR_CODES


CURSOR_UP_ONE: Final = "\x1b[1A"
ERASE_LINE: Final = "\x1b[2K"

DEFAULT_COLORS: Final = list(COLOR_CODES.values())

COLOR_RESET_CODE: Final = "\033[0m"
COLOR_CODE_REGEX: Final = re.compile(r"\033\[\d+m")


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
