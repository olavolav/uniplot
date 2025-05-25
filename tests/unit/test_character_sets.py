import pytest

from uniplot.character_sets import CharacterSet


def test_from_valid_string():
    valid_label = "braille"
    assert CharacterSet.from_string(valid_label)


def test_from_invalid_string():
    invalid_label = "strawB3RRY !!!"
    with pytest.raises(ValueError):
        CharacterSet.from_string(invalid_label)
