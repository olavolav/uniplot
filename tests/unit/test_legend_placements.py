import pytest

from uniplot.legend_placements import LegendPlacement


def test_from_valid_string():
    valid_label = "vertical"
    assert LegendPlacement.from_string(valid_label)


def test_from_invalid_string():
    invalid_label = "strawB3RRY !!!"
    with pytest.raises(ValueError):
        LegendPlacement.from_string(invalid_label)
