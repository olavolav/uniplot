"""Timezone-aware tick selection, formatting and placement."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from uniplot.axis_labels.datetime_label_set import DatetimeLabelSet
from uniplot.axis_labels.datetime_labels import datetime_labels

BERLIN = ZoneInfo("Europe/Berlin")


def test_labels_distinguish_both_folds_even_when_only_one_is_selected():
    values = [datetime(2026, 10, 25, 2, 0, tzinfo=BERLIN, fold=fold) for fold in (0, 1)]
    for selected in (values, values[:1], values[1:]):
        labels = np.array([v.timestamp() for v in selected]).astype("datetime64[s]")
        ls = DatetimeLabelSet(
            labels,
            values[0].timestamp(),
            values[1].timestamp() + 3600,
            available_space=80,
            timezone=BERLIN,
        )
        strings = ls._find_shortest_string_representation()
        assert strings == [
            "02:00+02:00" if v.fold == 0 else "02:00+01:00" for v in selected
        ]


def test_midnight_context_depends_on_view_not_only_selected_ticks():
    start = datetime(2026, 11, 2, 22, tzinfo=BERLIN)
    end = datetime(2026, 11, 3, 4, tzinfo=BERLIN)
    labels = np.array(
        [datetime(2026, 11, 3, h, tzinfo=BERLIN).timestamp() for h in (0, 3)]
    ).astype("datetime64[s]")
    ls = DatetimeLabelSet(
        labels, start.timestamp(), end.timestamp(), available_space=60, timezone=BERLIN
    )
    assert ls._find_shortest_string_representation() == ["11-03 00:00", "11-03 03:00"]


@pytest.mark.parametrize(
    "zone,start,hours",
    [
        ("Europe/Berlin", "2026-03-29 00:00", 10),
        ("Europe/Berlin", "2026-10-25 00:00", 5),
        ("Australia/Lord_Howe", "2026-04-05 00:00", 5),
        ("Asia/Kathmandu", "2026-01-15 09:00", 12),
    ],
)
@pytest.mark.parametrize("width", [30, 60, 100])
def test_local_ticks_are_valid_and_do_not_overlap(zone, start, hours, width):
    first = datetime.fromisoformat(start).replace(tzinfo=ZoneInfo(zone))
    last = first.astimezone(timezone.utc) + timedelta(hours=hours)
    ls = datetime_labels(
        first.timestamp(), last.timestamp(), width, timezone=ZoneInfo(zone)
    )
    assert ls is not None
    assert not ls.compute_if_render_does_overlap()
    assert np.all(np.diff(ls.labels.astype(float)) > 0)
    local = [datetime.fromtimestamp(t, ZoneInfo(zone)) for t in ls.labels.astype(float)]
    assert all(v.minute == 0 and v.second == 0 for v in local)
    if start == "2026-03-29 00:00":
        assert all(v.hour != 2 for v in local)


def test_local_midnight_ticks_follow_dst_instead_of_fixed_24_hour_steps():
    first = datetime(2026, 10, 23, tzinfo=BERLIN)
    last = datetime(2026, 10, 28, 12, tzinfo=BERLIN)
    ls = datetime_labels(first.timestamp(), last.timestamp(), 100, timezone=BERLIN)
    assert ls is not None
    local = [datetime.fromtimestamp(t, BERLIN) for t in ls.labels.astype(float)]
    assert all(v.hour == v.minute == v.second == 0 for v in local)
    assert 25 * 3600 in np.diff(ls.labels.astype(float))


def test_narrow_aware_axis_keeps_one_label_when_two_do_not_fit():
    start = datetime(2026, 10, 25, 2, 0, tzinfo=BERLIN, fold=1).timestamp()
    ls = datetime_labels(start, start + 1800, 12, timezone=BERLIN)
    assert ls is not None
    assert len(ls.labels) == 1
    assert "+01:00" in ls.render()[0]
    assert len(ls.render()[0]) <= 14


def test_only_second_fold_view_has_offset_labels():
    start = datetime(2026, 10, 25, 2, 10, tzinfo=BERLIN, fold=1).timestamp()
    ls = datetime_labels(start, start + 35 * 60, 60, timezone=BERLIN)
    assert ls is not None
    assert all("+01:00" in value for value in ls._find_shortest_string_representation())


def test_year_crossing_labels_include_the_year():
    start = datetime(2026, 12, 31, 22, tzinfo=BERLIN)
    end = datetime(2027, 1, 1, 4, tzinfo=BERLIN)
    labels = np.array([start.timestamp(), end.timestamp()]).astype("datetime64[s]")
    ls = DatetimeLabelSet(
        labels, start.timestamp(), end.timestamp(), available_space=80, timezone=BERLIN
    )
    assert ls._find_shortest_string_representation() == [
        "2026-12-31 22:00",
        "2027-01-01 04:00",
    ]


@pytest.mark.parametrize(
    "zone", ["Europe/Berlin", "Asia/Kathmandu", "Australia/Lord_Howe"]
)
def test_seeded_ranges_have_ordered_unique_readable_ticks(zone):
    rng = np.random.default_rng(53)
    for duration in (60, 3600, 12 * 3600, 3 * 86400, 90 * 86400, 3 * 365 * 86400):
        for vertical in (False, True):
            start = datetime(2026, 10, 25, tzinfo=timezone.utc).timestamp() + int(
                rng.integers(-86400, 86400)
            )
            space = 10 if vertical else int(rng.integers(30, 101))
            ls = datetime_labels(
                start,
                start + duration,
                space,
                vertical_direction=vertical,
                timezone=ZoneInfo(zone),
            )
            assert ls is not None
            positions = ls.labels.astype(float)
            assert np.all(np.diff(positions) > 0)
            assert np.all((positions >= start) & (positions <= start + duration))
            assert not ls.compute_if_render_does_overlap()
            strings = ls._find_shortest_string_representation()
            assert len(strings) == len(set(strings))
            assert all(strings)
            if not vertical:
                assert len(ls.render()[0]) <= space + 2


def test_offset_label_is_centered_on_its_tick_near_right_edge():
    value = datetime(2026, 10, 25, 2, tzinfo=BERLIN, fold=1)
    instant = value.timestamp()
    labels = np.array([instant]).astype("datetime64[s]")
    ls = DatetimeLabelSet(
        labels, instant - 3600, instant + 1, available_space=60, timezone=BERLIN
    )
    text = "02:00+01:00"
    # The tick is in the last plot column (59), plus the frame margin (1).
    assert ls.render()[0].index(text) + len(text) // 2 == 60
