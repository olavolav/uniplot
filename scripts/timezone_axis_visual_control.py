"""Manual timezone label gallery; run with `uv run python scripts/timezone_axis_visual_control.py`."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from uniplot import plot_to_string


def instants(start: datetime, hours: int) -> list[datetime]:
    utc = start.astimezone(timezone.utc)
    return [
        (utc + timedelta(hours=i)).astimezone(start.tzinfo) for i in range(hours + 1)
    ]


for zone, start, hours in [
    ("Europe/Berlin", (2026, 1, 15, 9), 12),
    ("Europe/Berlin", (2026, 11, 2, 22), 6),
    ("Europe/Berlin", (2026, 3, 29, 0), 9),
    ("Europe/Berlin", (2026, 10, 25, 0), 4),
    ("Europe/Berlin", (2026, 12, 31, 22), 6),
    ("Asia/Kathmandu", (2026, 1, 15, 9), 12),
    ("Australia/Lord_Howe", (2026, 4, 5, 0), 5),
]:
    values = instants(datetime(*start, tzinfo=ZoneInfo(zone)), hours)
    for width in (30, 60, 100):
        print(f"\n{zone}: {values[0]} to {values[-1]}, width={width}")
        print(plot_to_string(xs=values, ys=range(len(values)), width=width, height=4))
    print("\nVertical axis:")
    print(plot_to_string(ys=values, height=10, width=30))
