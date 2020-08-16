import numpy as np  # type: ignore

from uniplot.plot_elements import character_for_2by2_pixels


def test_empty_square():
    square = np.zeros([2, 2])
    assert character_for_2by2_pixels(square) == " "


def test_full_square():
    square = np.ones([2, 2])
    assert character_for_2by2_pixels(square) == "█"


def test_top_left_quarter_square():
    square = np.array([[1, 0], [0, 0]])
    assert character_for_2by2_pixels(square) == "▘"


def test_left_half_square():
    square = np.array([[1, 0], [1, 0]])
    assert character_for_2by2_pixels(square) == "▌"
