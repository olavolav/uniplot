import numpy as np  # type: ignore

from uniplot.discretizer import discretize, compute_y_at_middle_of_row


def test_correct_discretization_for_number():
    integer = discretize(x=2.1, x_min=1, x_max=3, steps=2)
    assert integer == 1


def test_correct_discretization_for_array():
    vector_float = np.array([0.01, 0.99, 1.01, 1.5, 1.99, 9.99])
    vector_integer = discretize(x=vector_float, x_min=0, x_max=10, steps=10)
    assert (vector_integer == np.array([0, 0, 1, 1, 1, 9])).all()


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
