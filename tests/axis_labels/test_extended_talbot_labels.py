import numpy as np  # type: ignore

from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels


def test_simple_labeling_case():
    ls = extended_talbot_labels(
        x_min=-0.5, x_max=2.5, available_space=40, vertical_direction=False
    )
    assert 0.0 in ls.labels
