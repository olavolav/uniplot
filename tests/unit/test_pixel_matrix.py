import numpy as np  # type: ignore

from uniplot.pixel_matrix import render, merge_on_top_with_shadow


###################
# Testing: render #
###################


def test_empty_plot():
    pixels = render(xs=[], ys=[], x_min=0, y_min=0, x_max=1, y_max=1, width=2, height=1)

    desired_pixels = np.array([[0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_single_pixel():
    pixels = render(
        xs=[0.5], ys=[0.5], x_min=0, y_min=0, x_max=1, y_max=1, width=1, height=1
    )

    desired_pixels = np.array([[1]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_diagonal():
    pixels = render(
        xs=[1, 2], ys=[1, 2], x_min=1, y_min=1, x_max=2.1, y_max=2.1, width=2, height=2
    )

    desired_pixels = np.array([[0, 1], [1, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


def test_diagonal_in_bigger_window():
    pixels = render(
        xs=[1, 2], ys=[1, 2], x_min=1, y_min=1, x_max=2.1, y_max=2.1, width=5, height=3
    )

    desired_pixels = np.array([[0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0]])
    np.testing.assert_array_equal(pixels, desired_pixels)


#####################################
# Testing: merge_on_top_with_shadow #
#####################################


def test_merge_two_empty_pixel_matrices():
    blank_pixels = np.array([[0, 0, 0], [0, 0, 0]])
    result = merge_on_top_with_shadow(
        low_layer=blank_pixels, high_layer=blank_pixels, width=3, height=2
    )

    np.testing.assert_array_equal(result, blank_pixels)


def test_merge_with_empty_lower_layer():
    some_pixels = np.array([[1, 0, 2], [0, 3, 4]])
    blank_pixels = np.array([[0, 0, 0], [0, 0, 0]])
    result = merge_on_top_with_shadow(
        low_layer=blank_pixels, high_layer=some_pixels, width=3, height=2
    )

    np.testing.assert_array_equal(result, some_pixels)


def test_merge_with_effective_shadow_small_patch():
    high_layer = np.array([[2, 0, 0], [0, 0, 0]])
    low_layer = np.array([[1, 1, 1], [1, 1, 1]])
    desired_layer = np.array([[2, 0, 1], [0, 0, 1]])

    result = merge_on_top_with_shadow(
        low_layer=low_layer, high_layer=high_layer, width=3, height=2
    )

    np.testing.assert_array_equal(result, desired_layer)


def test_merge_with_effective_shadow_bigger_patch():
    high_layer = np.array([[0, 2, 0], [2, 0, 0], [0, 0, 0],])
    low_layer = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1],])
    desired_layer = np.array([[0, 2, 0], [2, 0, 0], [0, 0, 1],])

    result = merge_on_top_with_shadow(
        low_layer=low_layer, high_layer=high_layer, width=3, height=3
    )

    np.testing.assert_array_equal(result, desired_layer)
