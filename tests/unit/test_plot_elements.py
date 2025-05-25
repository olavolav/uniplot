from uniplot.plot_elements import legend, plot_title, count_lines
from uniplot.legend_placements import LegendPlacement


###################
# Testing: legend #
###################


def test_single_legend_label():
    label_strings = ["A"]
    result = legend(
        legend_labels=label_strings, width=60, line_length_hard_cap=False, color=False
    )
    assert len(result) > 0
    assert "A" in result
    # Default is in a single line
    assert len(result.splitlines()) == 1


def test_enough_legend_labels_for_a_line_break():
    label_strings = ["A", "B", "c" * 10]
    result = legend(
        legend_labels=label_strings,
        width=12,
        line_length_hard_cap=False,
        color=False,
        legend_placement=LegendPlacement.AUTO,
    )
    assert len(result) > 0
    assert "A" in result
    assert len(result.splitlines()) == 2


def test_legend_labels_in_vertical_mode():
    label_strings = ["A", "B", "C"]
    result = legend(
        legend_labels=label_strings,
        width=19,
        line_length_hard_cap=False,
        color=False,
        legend_placement=LegendPlacement.VERTICAL,
    )
    assert len(result) > 0
    assert "A" in result
    assert len(result.splitlines()) == 3


#######################
# Testing: plot_title #
#######################


def test_short_title():
    title = "Headline!"
    result = plot_title(title, 60, None)
    # Make sure the title string is part of the result
    assert result.strip() == title
    # Make sure there is left padding applied
    assert result[:10] == " " * 10


def test_long_title():
    title = "Headline! In fact a mega headline in, compared to the small plot!"
    result = plot_title(title, 5, None)
    # Make sure no left padding was applied
    assert result.strip() == result


def test_long_title_with_hard_cap():
    title = "Headline! In fact a mega headline in, compared to the small plot!"
    result = plot_title(title, 100, 10)
    # Make sure no left padding was applied
    assert result.strip() == result


########################
# Testing: count_lines #
########################


def test_counting_a_single_line():
    text = "Hello Bob"
    assert count_lines(text) == 1


def test_counting_multiple_lines():
    text = "Hello Bob\nThe weather \nis:\t\tGREAT!\ntoday."
    assert count_lines(text) == 4


def test_counting_multiple_lines_with_ending_whitespace():
    text = "Hello Bob\nThe weather \r\n"
    assert count_lines(text) == 3
