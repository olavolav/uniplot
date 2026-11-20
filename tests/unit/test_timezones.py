"""Shared timezone semantics using native datetime inputs."""

import warnings
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from uniplot import histogram_to_string, plot_gen, plot_to_string
from uniplot.conversions import floatify
from uniplot.multi_series import MultiSeries
from uniplot.param_initializer import validate_and_transform_options

BERLIN = ZoneInfo("Europe/Berlin")


def _instants(
    start: datetime, count: int, step: timedelta = timedelta(hours=1)
) -> list[datetime]:
    utc = start.astimezone(timezone.utc)
    return [(utc + i * step).astimezone(start.tzinfo) for i in range(count)]


@pytest.mark.parametrize("axis", ["x", "y"])
def test_native_aware_datetimes_have_utc_coordinates_and_local_labels(axis):
    values = _instants(datetime(2026, 1, 15, 9, tzinfo=ZoneInfo("Asia/Tokyo")), 10)
    kwargs = {"ys": range(10), "xs": range(10), f"{axis}s": values}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        series = MultiSeries(**kwargs)
        output = plot_to_string(**kwargs, width=60, height=12)
    assert str(getattr(series, f"{axis}_timezone")) == "Asia/Tokyo"
    np.testing.assert_array_equal(
        getattr(series, f"{axis}s")[0], np.arange(10) * 3600 + values[0].timestamp()
    )
    labels = (
        output.splitlines()[-1]
        if axis == "x"
        else " ".join(
            row.split("│")[-1] for row in output.splitlines() if row.startswith("│")
        )
    )
    assert "12:00" in labels
    assert "00:00" not in labels


@pytest.mark.parametrize("axis", ["x", "y"])
@pytest.mark.parametrize("nested", [False, True])
def test_mixed_awareness_is_rejected(axis, nested):
    aware = datetime(2026, 1, 15, 12, tzinfo=BERLIN)
    values = (
        [[aware], [aware.replace(tzinfo=None)]]
        if nested
        else [aware, aware.replace(tzinfo=None)]
    )
    other = [[1], [2]] if nested else [1, 2]
    with pytest.raises(ValueError, match=f"{axis}.*aware.*naive"):
        MultiSeries(**{f"{axis}s": values, "ys" if axis == "x" else "xs": other})


def test_multiple_zones_warn_once_and_use_first_series_without_moving_points():
    first = _instants(datetime(2026, 1, 15, 9, tzinfo=ZoneInfo("Asia/Tokyo")), 3)
    second = [value.astimezone(BERLIN) for value in first]
    with pytest.warns(
        UserWarning, match="x.*different timezones.*Asia/Tokyo"
    ) as caught:
        series = MultiSeries(xs=[first, second], ys=[[1, 2, 3], [3, 2, 1]])
    assert len(caught) == 1
    assert str(series.x_timezone) == "Asia/Tokyo"
    np.testing.assert_array_equal(series.xs[0], series.xs[1])


def test_dst_offset_change_is_not_a_mixed_zone_warning():
    values = _instants(datetime(2026, 10, 25, tzinfo=BERLIN), 6)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        series = MultiSeries(xs=values, ys=range(6))
    np.testing.assert_array_equal(np.diff(series.xs[0]), np.full(5, 3600))


def test_missing_values_do_not_select_timezone_or_count_as_naive():
    value = datetime(2026, 1, 15, 12, tzinfo=BERLIN)
    series = MultiSeries(
        xs=[[], [None, np.datetime64("NaT"), value]], ys=[[], [1, 2, 3]]
    )
    assert series.x_timezone == BERLIN
    assert np.isnan(series.xs[1][:2]).all()
    assert series.xs[1][2] == value.timestamp()


def test_nonexistent_aware_wall_time_is_rejected():
    with pytest.raises(ValueError, match="nonexistent"):
        MultiSeries(xs=[datetime(2026, 3, 29, 2, 30, tzinfo=BERLIN)], ys=[1])


def test_naive_repeated_wall_times_stay_identical():
    values = [datetime(2026, 10, 25, 2, 30, tzinfo=BERLIN).replace(tzinfo=None)] * 2
    series = MultiSeries(xs=values, ys=[1, 2])
    assert series.x_timezone is None
    assert series.xs[0][0] == series.xs[0][1]


def test_aware_scalar_conversion_does_not_warn_or_lose_fold():
    values = [
        datetime(2026, 10, 25, 2, 30, tzinfo=BERLIN, fold=fold) for fold in (0, 1)
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert floatify(values[1]) - floatify(values[0]) == 3600


@pytest.mark.parametrize(
    "key", ["x_min", "x_max", "x_gridlines", "y_min", "y_max", "y_gridlines"]
)
def test_datetime_options_reject_awareness_mismatch(key):
    values = [datetime(2026, 1, 15, hour, tzinfo=BERLIN) for hour in (9, 12)]
    series = MultiSeries(xs=values, ys=values)
    naive = values[0].replace(tzinfo=None)
    value = [naive] if "gridlines" in key else naive
    with pytest.raises(ValueError, match="aware.*naive"):
        validate_and_transform_options(series, {key: value})


def test_aware_bounds_and_gridlines_normalize_without_warning():
    values = [datetime(2026, 1, 15, hour, tzinfo=BERLIN) for hour in (9, 12)]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        options = validate_and_transform_options(
            MultiSeries(xs=values, ys=values),
            {
                "x_min": values[0],
                "y_max": values[1],
                "x_gridlines": values,
                "y_gridlines": values,
            },
        )
    assert options.x_min == values[0].timestamp()
    assert options.y_max == values[1].timestamp()
    assert options.x_gridlines == options.y_gridlines == [v.timestamp() for v in values]


def test_fixed_offset_and_updates_keep_instants_and_pinned_bounds():
    tz = timezone(timedelta(hours=5, minutes=45))
    values = [datetime(2026, 1, 15, h, tzinfo=tz) for h in (9, 12, 15)]
    plot = plot_gen(xs=values, ys=[1, 2, 3], x_min=values[0], x_max=values[-1])
    plot.to_string()
    for _ in range(2):
        plot.set_data(xs=values, ys=[3, 2, 1])
        output = plot.to_string()
        assert "12:00" in output.splitlines()[-1]
        assert plot.options.x_min == values[0].timestamp()
        assert plot.options.x_max == values[-1].timestamp()


def test_automatic_padding_does_not_force_dates_on_a_single_day():
    values = _instants(datetime(2026, 10, 25, tzinfo=BERLIN), 17, timedelta(minutes=15))
    labels = plot_to_string(xs=values, ys=range(17), width=60).splitlines()[-1]
    assert "10-25" not in labels
    assert "02:00+02:00" in labels
    assert "02:00+01:00" in labels


def test_aware_fill_baseline_is_normalized_and_mismatches_are_rejected():
    values = [datetime(2026, 1, 15, h, tzinfo=BERLIN) for h in (9, 12)]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        options = validate_and_transform_options(
            MultiSeries(ys=values), {"fill": values[0]}
        )
    assert options.fill == [values[0].timestamp()]
    with pytest.raises(ValueError, match="aware.*naive"):
        validate_and_transform_options(
            MultiSeries(ys=values), {"fill": values[0].replace(tzinfo=None)}
        )


@pytest.mark.parametrize("axis", ["x", "y"])
@pytest.mark.parametrize("border", [None, "box"])
def test_long_timezone_labels_respect_hard_width_cap(axis, border):
    values = _instants(datetime(2026, 10, 25, tzinfo=BERLIN), 17, timedelta(minutes=15))
    kwargs = {"xs": range(17), "ys": range(17), f"{axis}s": values}
    output = plot_to_string(**kwargs, border=border, line_length_hard_cap=40)
    assert max(map(len, output.splitlines())) <= 40


def test_different_zones_in_one_list_warn_once():
    value = datetime(2026, 1, 15, 12, tzinfo=BERLIN)
    with pytest.warns(UserWarning, match="different timezones") as caught:
        series = MultiSeries(xs=[value, value.astimezone(timezone.utc)], ys=[1, 2])
    assert len(caught) == 1
    assert series.x_timezone == BERLIN
    assert series.xs[0][0] == series.xs[0][1]


def test_single_timestamp_gets_a_label():
    value = datetime(2026, 1, 15, 12, tzinfo=BERLIN)
    output = plot_to_string(xs=[value], ys=[1])
    assert "12:00" in output.splitlines()[-1]


def test_aware_series_on_naive_axis_rejects_aware_bounds():
    value = datetime(2026, 1, 15, 12, tzinfo=BERLIN)
    series = MultiSeries(xs=[value.replace(tzinfo=None)], ys=[1])
    with pytest.raises(ValueError, match="aware.*naive"):
        validate_and_transform_options(series, {"x_min": value})


def test_switching_between_aware_and_naive_data_drops_old_pinned_bounds():
    values = [datetime(2026, 1, 15, hour, tzinfo=BERLIN) for hour in (9, 12)]
    plot = plot_gen(xs=values, ys=[1, 2], x_min=values[0], x_max=values[-1])
    plot.to_string()
    naive = [value.replace(tzinfo=None) for value in values]
    plot.set_data(xs=naive, ys=[1, 2])
    plot.to_string()
    assert plot.options.x_max >= floatify(naive[-1])


def test_histogram_preserves_input_timezone():
    values = _instants(datetime(2026, 1, 15, 9, tzinfo=ZoneInfo("Asia/Tokyo")), 10)
    output = histogram_to_string(values, bins=5)
    assert "12:00" in output.splitlines()[-1]
    assert "00:00" not in output.splitlines()[-1]
