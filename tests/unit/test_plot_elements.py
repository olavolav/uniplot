import numpy as np  # type: ignore

from uniplot.plot_elements import character_for_2by2_pixels, xaxis_ticks


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


########################
# Testing: xaxis_ticks #
########################


def test_xaxis_labels_on_unit_interval():
    labels = xaxis_ticks(0, 1, 20)
    assert labels == " 0" + (" " * 18) + "1"


def test_xaxis_labels_on_small_symmetric_interval():
    # This test makes sure that issue #5 is solved
    labels = xaxis_ticks(-0.01, 0.01, 20)
    assert labels.split() == ["-0.01", "0.01"]


import numpy as np  # type: ignore
