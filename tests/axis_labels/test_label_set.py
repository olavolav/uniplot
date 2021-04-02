import numpy as np  # type: ignore

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
