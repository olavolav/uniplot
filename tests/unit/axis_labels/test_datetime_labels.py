import pytest
import numpy as np

from uniplot.axis_labels.datetime_labels import datetime_labels


def test_datetime_labeling_across_seconds():
    start_datetime = np.datetime64("2024-08-01T09:00:00").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-08-01T09:01:00").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 09:00:30 " in render


def test_datetime_labeling_across_seconds_with_nonzero_start():
    start_datetime = np.datetime64("2024-08-01T09:00:11").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-08-01T09:01:07").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 09:00:30 " in render


def test_datetime_labeling_across_minutes():
    start_datetime = np.datetime64("2024-08-01T09:00:00").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-08-01T09:45:00").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 09:30 " in render


def test_datetime_labeling_across_hours():
    start_datetime = np.datetime64("2024-08-01T09:00:00").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-08-01T15:00:00").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 10:00 " in render


def test_datetime_labeling_across_days():
    start_datetime = np.datetime64("2024-08-01").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-08-14").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert "2024-08-0" in render


def test_datetime_labeling_across_months():
    start_datetime = np.datetime64("2024-08-01").astype("datetime64[s]")
    end_datetime = np.datetime64("2024-11-15").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
        verbose=True,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 2024-09 " in render


def test_datetime_labeling_across_years():
    start_datetime = np.datetime64("2023-01-01").astype("datetime64[s]")
    end_datetime = np.datetime64("2025-08-14").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 2024 " in render


@pytest.mark.skip(reason="not yet implemented")
def test_datetime_labeling_across_centuries():
    start_datetime = np.datetime64("1000-01-01").astype("datetime64[s]")
    end_datetime = np.datetime64("3500-08-14").astype("datetime64[s]")
    ls = datetime_labels(
        x_min=start_datetime.astype(float),
        x_max=end_datetime.astype(float),
        available_space=60,
        vertical_direction=False,
    )
    assert ls is not None
    render = ls.render()[0]
    assert " 2000 " in render
