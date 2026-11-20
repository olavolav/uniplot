"""Integration with dateutil timezone objects."""

import warnings
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np

from uniplot import plot_to_string
from uniplot.multi_series import MultiSeries

BERLIN = ZoneInfo("Europe/Berlin")


def test_dateutil_timezone_objects_work_without_being_hashable():
    from dateutil.tz import gettz  # type: ignore

    zone = gettz("Europe/Berlin")
    values = [datetime(2026, 10, 25, 2, tzinfo=zone, fold=fold) for fold in (0, 1)]
    values.append(datetime(2026, 10, 25, 3, tzinfo=zone))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        output = plot_to_string(xs=values, ys=[1, 2, 3], width=60)
    assert "+02:00" in output.splitlines()[-1]
    assert "+01:00" in output.splitlines()[-1]


def test_utc_from_different_libraries_is_not_a_timezone_conflict():
    from dateutil.tz import UTC  # type: ignore

    value = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    values = [value, value.astimezone(ZoneInfo("UTC")), value.astimezone(UTC)]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        series = MultiSeries(xs=values, ys=[1, 2, 3])
    assert np.all(series.xs[0] == value.timestamp())
