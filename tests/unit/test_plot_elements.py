import numpy as np

from uniplot.plot_elements import character_for_2by4_pixels, plot_title, count_lines


######################################
# Testing: character_for_2by4_pixels #
######################################


def test_braille_empty_square():
    square = np.zeros([4, 2])
    assert character_for_2by4_pixels(square) == ""


def test_braille_full_square():
    square = np.ones([4, 2])
    assert character_for_2by4_pixels(square) == "⣿"


def test_braille_top_left_triagle():
    square = np.array([[1, 1], [1, 0], [0, 0], [0, 0]])
    assert character_for_2by4_pixels(square) == "⠋"


def test_braille_bottom_right_triagle():
    square = np.array([[0, 0], [0, 0], [0, 1], [1, 1]])
    assert character_for_2by4_pixels(square) == "⣠"


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
