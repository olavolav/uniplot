import numpy as np  # type: ignore

from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels


def test_simple_labeling_case():
    ls = extended_talbot_labels(
        x_min=-0.5, x_max=2.5, available_space=40, vertical_direction=False
    )
    assert 0.0 in ls.labels


def test_typical_labeling_case_with_small_range():
    """
    This is the result when plotting [1, 2, 3] using the default settings. We are testing both axis here.
    """
    ls = extended_talbot_labels(
        x_min=0.97, x_max=3.03, available_space=60, vertical_direction=False
    )
    assert np.array_equal(ls.labels, [1.0, 2.0, 3.0])

    ls = extended_talbot_labels(
        x_min=0.97, x_max=3.03, available_space=17, vertical_direction=True
    )
    assert np.array_equal(ls.labels, [1.0, 2.0, 3.0])
