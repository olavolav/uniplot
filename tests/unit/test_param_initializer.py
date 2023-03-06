import pytest

from uniplot.param_initializer import validate_and_transform_options
from uniplot.multi_series import MultiSeries


def test_passing_simple_list():
    series = MultiSeries(ys=[1, 2, 3])
    options = validate_and_transform_options(series=series)
    assert options.interactive == False


def test_lines_option_with_simple_list():
    series = MultiSeries(ys=[1, 2, 3])
    options = validate_and_transform_options(series=series, kwargs={"lines": True})
    assert options.lines == [True]


def test_lines_option_with_multiple_lists():
    series = MultiSeries(ys=[[1, 2, 3], [100, 1000, 10000]])
    options = validate_and_transform_options(
        series=series, kwargs={"lines": [False, True]}
    )
    assert options.lines == [False, True]


def test_invalid_lines_option_with_multiple_lists():
    series = MultiSeries(ys=[[1, 2, 3], [100, 1000, 10000]])
    with pytest.raises(ValueError):
        validate_and_transform_options(series=series, kwargs={"lines": [False]})
