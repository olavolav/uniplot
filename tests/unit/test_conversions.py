import numpy as np
from numpy.testing import assert_equal

from uniplot.conversions import convert_matrix_to_rows_of_submatrices


#################################################
# testing: convert_matrix_to_rows_of_submatices #
#################################################


def test_convert_for_box_submatrices():
    x = np.array([[0, 1, 2, 3], [0, 4, 5, 6], [1, 7, 8, 9], [2, 8, 9, 0]])
    y = convert_matrix_to_rows_of_submatrices(x, 2, 2)
    y_true = np.array([[[0, 1, 0, 4], [2, 3, 5, 6]], [[1, 7, 2, 8], [8, 9, 9, 0]]])
    assert_equal(y, y_true)


def test_convert_for_ascii_submatrices():
    x = np.array([[0, 1, 2], [0, 4, 5], [1, 7, 8]])
    y = convert_matrix_to_rows_of_submatrices(x, 1, 1)
    y_true = np.array([[[0], [1], [2]], [[0], [4], [5]], [[1], [7], [8]]])
    assert_equal(y, y_true)


def test_convert_for_braille_submatrices():
    x = np.array([[0, 1, 3, 4], [0, 4, 6, 7], [1, 7, 8, 9], [7, 7, 8, 8]])
    y = convert_matrix_to_rows_of_submatrices(x, 2, 4)
    y_true = np.array([[[0, 1, 0, 4, 1, 7, 7, 7], [3, 4, 6, 7, 8, 9, 8, 8]]])
    assert_equal(y, y_true)
