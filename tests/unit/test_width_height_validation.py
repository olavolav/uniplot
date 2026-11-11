import pytest

from uniplot.multi_series import MultiSeries
from uniplot.param_initializer import validate_and_transform_options


@pytest.mark.parametrize("key", ["width", "height"])
@pytest.mark.parametrize("bad_value", [0, -1, -100, 2.5, "60", True, None])
def test_invalid_width_height_option_raises_value_error(key, bad_value):
    series = MultiSeries(ys=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        validate_and_transform_options(series=series, kwargs={key: bad_value})
    assert f"Invalid '{key}' option" in str(e.value)


@pytest.mark.parametrize("key", ["width", "height"])
@pytest.mark.parametrize("good_value", [1, 20, 200])
def test_valid_width_height_option_is_accepted(key, good_value):
    series = MultiSeries(ys=[1, 2, 3])
    options = validate_and_transform_options(series=series, kwargs={key: good_value})
    assert getattr(options, key) == good_value
