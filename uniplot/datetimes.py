"""Datetime normalization and local calendar conversion, shared by both axes.

Aware values are instants; naive values are wall-clock coordinates. Never use
the machine's timezone to convert one into the other.
"""

import warnings
from dataclasses import dataclass
from datetime import date, datetime, timezone, tzinfo
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
from numpy.typing import NDArray


class _HashableTimezone(tzinfo):
    """Preserve third-party tzinfo rules while allowing bounded label caches.

    dateutil tzfile objects implement equality but are unhashable. A constant
    hash preserves that equality contract without guessing their IANA names.
    """

    def __init__(self, zone: tzinfo):
        self.zone = zone

    def __hash__(self) -> int:
        return 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _HashableTimezone) and self.zone == other.zone

    def __str__(self) -> str:
        return str(self.zone)

    def utcoffset(self, dt):
        return self.zone.utcoffset(dt.replace(tzinfo=self.zone) if dt else None)

    def dst(self, dt):
        return self.zone.dst(dt.replace(tzinfo=self.zone) if dt else None)

    def tzname(self, dt):
        return self.zone.tzname(dt.replace(tzinfo=self.zone) if dt else None)

    def fromutc(self, dt):
        return self.zone.fromutc(dt.replace(tzinfo=self.zone)).replace(tzinfo=self)


def canonical_timezone(zone: tzinfo) -> tzinfo:
    """Use fold-aware IANA rules, including for pandas' legacy pytz zones."""
    name = getattr(zone, "key", None) or getattr(zone, "zone", None)
    if name in ("UTC", "Etc/UTC", "GMT", "Etc/GMT") or (
        type(zone).__module__.startswith("dateutil") and type(zone).__name__ == "tzutc"
    ):
        return timezone.utc
    if name:
        return ZoneInfo(name)
    # pytz fixed offsets have no IANA key and cannot localize via replace().
    if type(zone).__module__.startswith("pytz"):
        offset = zone.utcoffset(None)
        if offset is not None:
            return timezone(offset)
    try:
        hash(zone)
    except TypeError:
        return _HashableTimezone(zone)
    return zone


def is_missing(value: Any) -> bool:
    if value is None or type(value).__name__ in ("NaTType", "NAType"):
        return True
    if isinstance(value, np.datetime64):
        return bool(np.isnat(value))
    return isinstance(value, (float, np.floating)) and bool(np.isnan(value))


def datetime_timezone(value: Any) -> tzinfo | None:
    if (
        isinstance(value, datetime)
        and not is_missing(value)
        and value.utcoffset() is not None
        and value.tzinfo is not None
    ):
        return canonical_timezone(value.tzinfo)
    return None


def datetime_seconds(value: Any) -> float:
    """Seconds at existing datetime64[s] precision, without NumPy tz warnings."""
    if is_missing(value):
        return float("nan")
    zone = datetime_timezone(value)
    if zone is not None:
        utc = value.astimezone(timezone.utc)
        back = utc.astimezone(zone)
        if back.replace(tzinfo=None) != value.replace(tzinfo=None):
            raise ValueError(
                f"Datetime {value} is a nonexistent local time in {zone}. "
                "Supply a valid timezone-aware datetime (or convert from UTC)."
            )
        value = utc.replace(tzinfo=None)
    return float(np.datetime64(value, "s").astype(float))


@dataclass
class DatetimeSeries:
    values: NDArray
    # None here means a valid naive value; missing values contribute no entries.
    zones: list[tzinfo | None]


def normalize_datetime_series(series: Any) -> DatetimeSeries | None:
    """Recognize dates before an array conversion can discard timezone metadata.

    Pandas and Polars remain optional: their typed arrays provide fast paths;
    object arrays and ordinary sequences use the scalar normalization above.
    """
    accessor = getattr(series, "dt", series)
    zone = getattr(accessor, "tz", None)
    if zone is not None:  # pandas DatetimeIndex / Series
        dates = np.asarray(accessor.tz_convert(None)).astype("datetime64[s]")
    else:
        zone_name = getattr(getattr(series, "dtype", None), "time_zone", None)
        zone = ZoneInfo(zone_name) if zone_name else None  # Polars Datetime
        dates = np.asarray(series)
    if np.issubdtype(dates.dtype, np.datetime64):
        dates = dates.astype("datetime64[s]")
        valid = ~np.isnat(dates)
        values = dates.astype(float)
        values[~valid] = np.nan
        zones = [canonical_timezone(zone) if zone else None] if valid.any() else []
        return DatetimeSeries(values, zones)
    if np.issubdtype(dates.dtype, np.number):
        return None

    scalar_values: list[float] = []
    zones = []
    for value in dates:
        if is_missing(value):
            scalar_values.append(float("nan"))
            continue
        if isinstance(value, str):
            # Handle offset-bearing ISO strings without NumPy discarding offsets.
            try:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                try:
                    value = np.datetime64(value)
                except ValueError:
                    return None
        if not isinstance(value, (date, np.datetime64)):
            return None
        if not is_missing(value):
            zones.append(datetime_timezone(value))
        scalar_values.append(datetime_seconds(value))
    return DatetimeSeries(np.array(scalar_values, dtype=float), zones)


def axis_timezone(rows: list[DatetimeSeries], axis: str) -> tzinfo | None:
    zones = [zone for row in rows for zone in row.zones]
    if not zones:
        return None
    first = zones[0]
    if any((zone is None) != (first is None) for zone in zones):
        raise ValueError(
            f"{axis} axis mixes timezone-aware and naive datetimes. "
            "Supply all datetimes with timezones, or all without timezones; "
            "localize naive values before plotting if they represent instants."
        )
    if any(zone != first for zone in zones):
        warnings.warn(
            f"{axis} axis contains different timezones; labels use {first} "
            "from the first series. Convert inputs to a common timezone "
            "before plotting to choose another display timezone.",
            UserWarning,
            stacklevel=3,
        )
    return first


def validate_datetime_option(value: Any, zone: tzinfo | None, name: str) -> None:
    if (
        isinstance(value, (date, np.datetime64))
        and not is_missing(value)
        and (datetime_timezone(value) is None) != (zone is None)
    ):
        raise ValueError(
            f"{name} mixes timezone-aware and naive datetimes with its axis. "
            "Use the same awareness as the data, or numeric axis coordinates."
        )


def pad_datetime_bound(value: float, padded: float, zone: tzinfo | None) -> float:
    """Don't add a second calendar day solely through automatic plot padding."""
    if zone is not None and (
        datetime.fromtimestamp(value, zone).date()
        != datetime.fromtimestamp(padded, zone).date()
    ):
        return value
    return padded


@lru_cache(maxsize=4096)
def utc_to_local_seconds(seconds: int, zone: tzinfo) -> int:
    offset = datetime.fromtimestamp(seconds, zone).utcoffset()
    assert offset is not None
    return seconds + int(offset.total_seconds())


@lru_cache(maxsize=4096)
def local_to_utc_seconds(seconds: int, zone: tzinfo) -> tuple[int, ...]:
    """Return zero, one or two instants for a local calendar tick."""
    local = datetime.fromtimestamp(seconds, timezone.utc)
    candidates = set()
    for fold in (0, 1):
        instant = int(local.replace(tzinfo=zone, fold=fold).timestamp())
        if utc_to_local_seconds(instant, zone) == seconds:
            candidates.add(instant)
    return tuple(sorted(candidates))


def utc_to_local(values: NDArray, zone: tzinfo) -> NDArray:
    return np.array(
        [
            utc_to_local_seconds(int(t), zone)
            for t in values.astype("datetime64[s]").astype(int)
        ],
        dtype="datetime64[s]",
    )


def local_to_utc(values: NDArray, zone: tzinfo) -> NDArray:
    return np.unique(
        np.array(
            [
                t
                for value in values.astype("datetime64[s]").astype(int)
                for t in local_to_utc_seconds(int(value), zone)
            ],
            dtype="datetime64[s]",
        )
    )
