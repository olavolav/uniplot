import sys
from datetime import datetime
from typing import Any, Final

import numpy as np
from numpy.typing import NDArray

from uniplot import colors
from uniplot.character_sets import CharacterSet
from uniplot.legend_placements import LegendPlacement

CURSOR_UP_ONE: Final = "\x1b[1A"
ERASE_LINE: Final = "\x1b[2K"

LEGEND_VERTICAL_SPACING: Final = 3


def legend(
    legend_labels: list[str],
    width: int,
    line_length_hard_cap: int | None,
    color: list[colors.Color] | None,
    force_ascii_characters: list[str] | None = None,
    character_set: CharacterSet = CharacterSet.BLOCK,
    legend_placement: LegendPlacement = LegendPlacement.AUTO,
    border_width: int = 2,
) -> str:
    """
    Assemble a legend that shows the color of the different curves.
    """
    if len(legend_labels) == 0:
        return ""
    if force_ascii_characters is None:
        force_ascii_characters = []

    label_strings: list[str] = []
    for i, legend in enumerate(legend_labels):
        symbol: str = "█"
        if character_set == CharacterSet.ASCII:
            symbol = force_ascii_characters[i % len(force_ascii_characters)]
        elif character_set == CharacterSet.BRAILLE:
            symbol = "⣿"

        label_string = (
            _colorize_char(symbol * 2, i + 1, color) + " " + str(legend).strip()
        )
        label_strings.append(label_string)

    if legend_placement == LegendPlacement.AUTO:
        # If possible, group multiple labels into a single line
        i = 1  # start at 2nd label
        while i < len(label_strings):
            len_previous_label = _effective_len(label_strings[i - 1])
            len_current_label = _effective_len(label_strings[i])
            if len_previous_label + LEGEND_VERTICAL_SPACING + len_current_label < width:
                # We can merge these lines
                label_strings[i - 1] = (
                    label_strings[i - 1]
                    + (" " * LEGEND_VERTICAL_SPACING)
                    + label_strings[i]
                )
                del label_strings[i]
            else:
                # We cannot merge these lines
                i += 1

    full_label_string = "\n".join(label_strings)

    if legend_placement == LegendPlacement.AUTO:
        return _center_each_line_if_possible(
            full_label_string, width + border_width, line_length_hard_cap
        )
    return _center_block_if_possible(
        full_label_string, width + border_width, line_length_hard_cap
    )


def plot_title(
    title: str,
    width: int,
    line_length_hard_cap: int | None,
    border_width: int = 2,
) -> str:
    """
    Returns the centered title string.

    Note that this assumes that `title` is not `None`.
    """
    return _center_block_if_possible(title, width + border_width, line_length_hard_cap)


def erase_previous_lines(nr_lines: int) -> None:
    """
    This used terminal codes to erase the last `nr_lines` lines.
    """
    for _ in range(nr_lines):
        sys.stdout.write(ERASE_LINE)
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def prepare_histogram(
    multi_series: Any,
    bins: int = 20,
    bins_min: float | None = None,
    bins_max: float | None = None,
) -> tuple[list, list]:
    bins_min_real: float = bins_min if bins_min is not None else multi_series.y_min()
    bins_max_real: float = bins_max if bins_max is not None else multi_series.y_max()
    assert bins_max_real > bins_min_real

    # Depending on whether the bin limits were supplied as arguments, expand
    # the width automatically
    delta: float = bins_max_real - bins_min_real
    if bins_min is None:
        bins_min_real = bins_min_real - 0.1 * delta
    if bins_max is None:
        bins_max_real = bins_max_real + 0.1 * delta

    # Compute bin edges
    bin_edges = [
        bins_min_real + i * (bins_max_real - bins_min_real) / bins
        for i in range(bins + 1)
    ]

    xs_histo_series = []
    ys_histo_series = []
    for s in multi_series.ys:
        xs_barchart, ys_barchart = compute_bar_chart_histogram_points(s, bin_edges)
        # We bin the internal float representation, so for a datetime series the
        # bin edges come back as raw epoch seconds. Cast them back to
        # `datetime64[s]` so the downstream plot re-detects the x-axis as a time
        # series and renders date labels instead of raw numbers.
        if multi_series.y_is_time_series:
            if multi_series.y_timezone is not None:
                xs_barchart = np.array(
                    [
                        datetime.fromtimestamp(t, multi_series.y_timezone)
                        for t in xs_barchart
                    ],
                    dtype=object,
                )
            else:
                xs_barchart = xs_barchart.astype("datetime64[s]")
        xs_histo_series.append(xs_barchart)
        ys_histo_series.append(ys_barchart)

    return (xs_histo_series, ys_histo_series)


def compute_bar_chart_histogram_points(
    values: NDArray, bin_edges: list[float]
) -> tuple:
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


def _center_each_line_if_possible(
    text: str, width: int, line_length_hard_cap: int | None
) -> str:
    lines = text.splitlines()
    centered_lines = [
        _center_block_if_possible(
            line, width=width, line_length_hard_cap=line_length_hard_cap
        )
        for line in lines
    ]
    return "\n".join(centered_lines)


def _center_block_if_possible(
    text: str, width: int, line_length_hard_cap: int | None
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
    return colors.COLOR_CODE_REGEX.sub("", text)


def _effective_len(text: str) -> int:
    return len(_text_without_control_chars(text))


def _colorize_char(
    char: str, color_nr: int, color_mode: list[colors.Color] | None
) -> str:
    if char == "" or (not color_mode) or color_nr < 1:
        return char
    color = color_mode[(color_nr - 1) % len(color_mode)]
    return color.colorize(char)


def _histogram_to_bar_chart_points(bin_edges, counts) -> tuple:
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
