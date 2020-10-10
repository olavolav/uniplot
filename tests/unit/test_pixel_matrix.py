import numpy as np  # type: ignore

from uniplot.pixel_matrix import render, merge_on_top


###################
# Testing: render #
###################


def test_empty_plot():
    pixels = render(
        xs=np.array([]),
        ys=np.array([]),
        x_min=0,
        y_min=0,
        x_max=1,
        y_max=1,
        width=2,
        height=1,
    )

    desired_pixels = np.array([[0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_single_pixel():
    pixels = render(
        xs=np.array([0.5]),
        ys=np.array([0.5]),
        x_min=0,
        y_min=0,
        x_max=1,
        y_max=1,
        width=1,
        height=1,
    )

    desired_pixels = np.array([[1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_diagonal():
    pixels = render(
        xs=np.array([1, 2]),
        ys=np.array([1, 2]),
        x_min=1,
        y_min=1,
        x_max=2.1,
        y_max=2.1,
        width=2,
        height=2,
    )

    desired_pixels = np.array([[0, 1], [1, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_diagonal_in_bigger_window():
    pixels = render(
        xs=np.array([1, 2]),
        ys=np.array([1, 2]),
        x_min=1,
        y_min=1,
        x_max=2.1,
        y_max=2.1,
        width=5,
        height=3,
    )

    desired_pixels = np.array([[0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_diagonal_line():
    pixels = render(
        xs=np.array([1, 2]),
        ys=np.array([1, 2]),
        x_min=1,
        y_min=1,
        x_max=2.1,
        y_max=2.1,
        width=5,
        height=5,
        lines=True,
    )

    desired_pixels = np.array(
        [
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]
    )
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_horizontal_line():
    pixels = render(
        xs=np.array([1, 2]),
        ys=np.array([1, 1]),
        x_min=1,
        y_min=1,
        x_max=2.1,
        y_max=2.1,
        width=5,
        height=3,
        lines=True,
    )

    desired_pixels = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_vertical_line():
    pixels = render(
        xs=np.array([1, 1]),
        ys=np.array([1, 2]),
        x_min=1,
        y_min=1,
        x_max=2.1,
        y_max=2.1,
        width=2,
        height=4,
        lines=True,
    )

    desired_pixels = np.array([[1, 0], [1, 0], [1, 0], [1, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_no_mysterious_extra_vertical_lines():
    """
    This test is to make sure that issue #2 is fixed.
    """
    width = 60
    height = 17
    pixels = render(
        xs=np.array([1, 1]),
        ys=np.array([0, 1]),
        x_min=3,
        y_min=0,
        x_max=6,
        y_max=1.1,
        width=width,
        height=height,
        lines=True,
    )

    desired_pixels = np.zeros((height, width), dtype=int)
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_forward_line_with_steep_upward_slope():
    pixels = render(
        xs=np.array([1, 20]),
        ys=np.array([1, 200]),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=2,
        height=4,
        lines=True,
    )

    desired_pixels = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_forward_line_with_shallow_upward_slope():
    pixels = render(
        xs=np.array([1, 20]),
        ys=np.array([1, 200]),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=4,
        height=2,
        lines=True,
    )

    desired_pixels = np.array([[0, 0, 1, 1], [1, 1, 0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_forward_line_with_steep_downward_slope():
    pixels = render(
        xs=np.array([1, 20]),
        ys=np.array([200, 1]),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=2,
        height=4,
        lines=True,
    )

    desired_pixels = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_forward_line_with_shallow_downward_slope():
    pixels = render(
        xs=np.array([1, 20]),
        ys=np.array([200, 1]),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=4,
        height=2,
        lines=True,
    )

    desired_pixels = np.array([[1, 1, 0, 0], [0, 0, 1, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_backward_line_with_steep_upward_slope():
    pixels = render(
        xs=np.flip(np.array([1, 20])),
        ys=np.flip(np.array([1, 200])),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=2,
        height=4,
        lines=True,
    )

    desired_pixels = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_backward_line_with_shallow_upward_slope():
    pixels = render(
        xs=np.flip(np.array([1, 20])),
        ys=np.flip(np.array([1, 200])),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=4,
        height=2,
        lines=True,
    )

    desired_pixels = np.array([[0, 0, 1, 1], [1, 1, 0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_backward_line_with_steep_downward_slope():
    pixels = render(
        xs=np.flip(np.array([1, 20])),
        ys=np.flip(np.array([200, 1])),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=2,
        height=4,
        lines=True,
    )

    desired_pixels = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_backward_line_with_shallow_downward_slope():
    pixels = render(
        xs=np.flip(np.array([1, 20])),
        ys=np.flip(np.array([200, 1])),
        x_min=1,
        y_min=1,
        x_max=20.1,
        y_max=200.1,
        width=4,
        height=2,
        lines=True,
    )

    desired_pixels = np.array([[1, 1, 0, 0], [0, 0, 1, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_draw_triangular_line():
    pixels = render(
        xs=np.array([1, 3, 2, 1]),
        ys=np.array([1, 1, 2, 1]),
        x_min=1,
        y_min=1,
        x_max=3.01,
        y_max=2.01,
        width=5,
        height=3,
        lines=True,
    )

    desired_pixels = np.array([[0, 0, 1, 0, 0], [0, 1, 0, 1, 0], [1, 1, 1, 1, 1],])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_lines_outside_of_the_field_of_view():
    pixels = render(
        xs=np.array([1, 3, 2, 1]),
        ys=np.array([1, 1, 2, 1]),
        x_min=1.9,
        y_min=1.5,
        x_max=2.1,
        y_max=1.51,
        width=5,
        height=3,
        lines=True,
    )

    desired_pixels = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_lines_with_steep_ends_due_to_point_near_pixel_edges():
    pixels = render(
        xs=np.array([1.99, 3.01]),
        ys=np.array([1.01, 3.99]),
        x_min=0,
        y_min=0,
        x_max=5,
        y_max=5,
        width=5,
        height=5,
        lines=True,
    )

    # Despite the fact that we extend the lines to the end points (see issue #4), we
    # do not wish there to be extensions beyond the end points.
    desired_pixels = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    np.testing.assert_array_equal(pixels, desired_pixels)


#########################
# Testing: merge_on_top #
#########################


def test_merge_two_empty_pixel_matrices():
    blank_pixels = np.array([[0, 0, 0], [0, 0, 0]])
    result = merge_on_top(
        low_layer=blank_pixels, high_layer=blank_pixels, width=3, height=2
    )

    np.testing.assert_array_equal(result, blank_pixels)


def test_merge_with_empty_lower_layer():
    some_pixels = np.array([[1, 0, 2], [0, 3, 4]])
    blank_pixels = np.array([[0, 0, 0], [0, 0, 0]])
    result = merge_on_top(
        low_layer=blank_pixels, high_layer=some_pixels, width=3, height=2
    )

    np.testing.assert_array_equal(result, some_pixels)


def test_merge_with_effective_shadow_small_patch():
    high_layer = np.array([[2, 0, 0], [0, 0, 0]])
    low_layer = np.array([[1, 1, 1], [1, 1, 1]])
    desired_layer = np.array([[2, 0, 1], [0, 0, 1]])

    result = merge_on_top(
        low_layer=low_layer, high_layer=high_layer, width=3, height=2, with_shadow=True
    )

    np.testing.assert_array_equal(result, desired_layer)


def test_merge_with_effective_shadow_bigger_patch():
    high_layer = np.array([[0, 2, 0], [2, 0, 0], [0, 0, 0],])
    low_layer = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1],])
    desired_layer = np.array([[0, 2, 0], [2, 0, 0], [0, 0, 1],])

    result = merge_on_top(
        low_layer=low_layer, high_layer=high_layer, width=3, height=3, with_shadow=True
    )

    np.testing.assert_array_equal(result, desired_layer)


def test_merge_without_shadow_bigger_patch():
    high_layer = np.array([[0, 2, 0], [2, 0, 0], [0, 0, 0],])
    low_layer = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1],])
    desired_layer = np.array([[0, 2, 1], [2, 1, 1], [1, 1, 1],])

    result = merge_on_top(
        low_layer=low_layer, high_layer=high_layer, width=3, height=3, with_shadow=False
    )

    np.testing.assert_array_equal(result, desired_layer)
