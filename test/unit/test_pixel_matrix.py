import numpy as np  # type: ignore

from textplot.pixel_matrix import render


def test_empty_plot():
    pixels = render(xs=[], ys=[], x_min=0, y_min=0, x_max=1, y_max=1, width=2, height=1)

    desired_pixels = np.array([[0], [0]])
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

    desired_pixels = np.array([[1, 0], [0, 1]])
    np.testing.assert_array_equal(pixels, desired_pixels)
