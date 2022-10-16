import numpy as np  # type: ignore

from uniplot.discretizer import (
    discretize,
    discretize_array,
    compute_y_at_middle_of_row,
    invert_discretize,
    invert_discretize_array,
)


####################
# Test: discretize #
####################


def test_correct_discretization_for_number():
    integer = discretize(x=2.1, x_min=1, x_max=3, steps=2)
    assert integer == 1


def test_correct_discretization_for_array():
    vector_float = np.array([0.01, 0.99, 1.01, 1.5, 1.99, 9.99])
    vector_integer = discretize_array(x=vector_float, x_min=0, x_max=10, steps=10)
    assert (vector_integer == np.array([0, 0, 1, 1, 1, 9])).all()


def test_correct_discretization_for_array_with_nans_should_be_negative_one():
    vector_float = np.array([0.1, np.nan, 9.9])
    vector_integer = discretize_array(x=vector_float, x_min=0, x_max=10, steps=10)
    assert (vector_integer == np.array([0, -1, 9])).all()


####################################
# Test: compute_y_at_middle_of_row #
####################################


def test_compute_y_at_middle_of_row_simple_case():
    y_level = compute_y_at_middle_of_row(
        height_index_from_top=1, y_min=0, y_max=10, height=3
    )
    y_level_as_designed = 5
    assert abs(y_level - y_level_as_designed) < 0.01


def test_compute_y_at_middle_of_row_complex_case():
    y_level = compute_y_at_middle_of_row(
        height_index_from_top=1, y_min=5, y_max=10, height=10
    )
    y_level_as_designed = 9.25
    assert abs(y_level - y_level_as_designed) < 0.01


###########################
# Test: invert_discretize #
###########################


def test_invert_discretize_with_single_index():
    level = invert_discretize(2, minimum=0, maximum=1, nr_bins=3)
    level_as_designed = 5 / 6
    assert abs(level - level_as_designed) < 0.01


def test_invert_discretize_with_list_of_indices():
    levels = invert_discretize_array([0, 9, 1], minimum=0, maximum=10, nr_bins=10)
    levels_as_designed = [1 / 2, 9 + 1 / 2, 3 / 2]

    assert abs(levels[0] - levels_as_designed[0]) < 0.01
    assert abs(levels[1] - levels_as_designed[1]) < 0.01
    assert abs(levels[2] - levels_as_designed[2]) < 0.01
