"""Integration with pytz timezone objects."""

import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from uniplot import plot_to_string

BERLIN = ZoneInfo("Europe/Berlin")


def test_legacy_pytz_datetimes_keep_zone_rules_across_dst():
    pytz = pytest.importorskip("pytz")
    zone = pytz.timezone("Europe/Berlin")
    naive = datetime(2026, 10, 25, 2, tzinfo=BERLIN).replace(tzinfo=None)
    values = [zone.localize(naive, is_dst=dst) for dst in (True, False)]
    values.append(zone.localize(naive.replace(hour=3)))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        output = plot_to_string(xs=values, ys=[1, 2, 3], width=60)
    assert "+02:00" in output.splitlines()[-1]
    assert "+01:00" in output.splitlines()[-1]
