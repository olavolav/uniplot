import numpy as np  # type: ignore

from uniplot.param_initializer import validate_and_transform_options
from uniplot.multi_series import MultiSeries


def test_passing_simple_list():
    series = MultiSeries(ys=[1, 2, 3])
    options = validate_and_transform_options(series=series)

    assert options.interactive == False


if __name__ == "__main__":
    test_passing_simple_list()
