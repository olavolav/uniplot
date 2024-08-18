import numpy as np

from uniplot.axis_labels.label_set import LabelSet


def test_redering_to_string():
    labels = np.array([0, 1, 2])
    ls = LabelSet(
        labels, x_min=-0.5, x_max=2.5, available_space=30, vertical_direction=False
    )
    render = ls.render()
    assert len(render) == 1
    assert len(render[0]) >= 15
    assert " 0 " in render[0]
    assert ls.compute_if_render_does_overlap() is False


def test_redering_detects_overlap():
    labels = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    ls = LabelSet(
        labels, x_min=-0.5, x_max=2.5, available_space=3, vertical_direction=False
    )
    assert ls.compute_if_render_does_overlap() is True


def test_redering_to_string_with_unit():
    labels = np.array([0, 1, 2])
    ls = LabelSet(
        labels,
        x_min=-0.5,
        x_max=2.5,
        available_space=30,
        unit=" apples",
        vertical_direction=False,
    )
    render = ls.render()
    assert len(render) == 1
    assert len(render[0]) >= 15
    assert " 0 apples" in render[0]
    assert ls.compute_if_render_does_overlap() is False


def test_floating_point_wrapping_issue():
    """
    This is covering issue #15. It tests that the right number of digits are displayed even is only a part of the labels have digits on both sides of the decimal point.
    """
    ls = LabelSet(
        labels=np.array([-1.4, -0.9, -0.4]),
        x_min=-1.846526999372103,
        x_max=-0.1651564799721942,
        available_space=17,
        vertical_direction=True,
    )
    render = ls.render()
    assert "-1.4" in render
    assert "-0.4" in render
