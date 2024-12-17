import numpy as np

from uniplot.plot_elements import character_for_2by2_pixels, character_for_2by4_pixels


######################################
# Testing: character_for_2by2_pixels #
######################################


def test_empty_square():
    square = np.zeros([2, 2])
    assert character_for_2by2_pixels(square) == ""


def test_full_square():
    square = np.ones([2, 2])
    assert character_for_2by2_pixels(square) == "█"


def test_top_left_quarter_square():
    square = np.array([[1, 0], [0, 0]])
    assert character_for_2by2_pixels(square) == "▘"


def test_left_half_square():
    square = np.array([[1, 0], [1, 0]])
    assert character_for_2by2_pixels(square) == "▌"


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
