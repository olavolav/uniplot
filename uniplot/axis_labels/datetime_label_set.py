import re
from datetime import datetime, tzinfo

import numpy as np
from numpy.typing import NDArray

from uniplot.axis_labels.label_set import LEFT_MARGIN_FOR_HORIZONTAL_AXIS, LabelSet
from uniplot.datetimes import local_to_utc_seconds, utc_to_local


class DatetimeLabelSet(LabelSet):
    """
    A label set for datetime values like timestamps.
    """

    def __init__(
        self,
        labels: NDArray,
        x_min: float,
        x_max: float,
        available_space: int = 17,
        unit: str = "",
        log: bool = False,
        vertical_direction: bool = False,
        left_margin: int = LEFT_MARGIN_FOR_HORIZONTAL_AXIS,
        timezone: tzinfo | None = None,
    ):
        self.timezone = timezone
        # Note: unit scaling (`unit_scaling`) does not apply to timestamps, so
        # this class intentionally does not expose that option and lets the base
        # class default it to off.
        super().__init__(
            labels,
            x_min,
            x_max,
            available_space,
            unit=unit,
            log=log,
            vertical_direction=vertical_direction,
            left_margin=left_margin,
        )
        # For convenience, make sure we have the bounds also available as
        # datetime objects.
        self.x_min_as_dt = np.float64(self.x_min).astype("datetime64[s]")
        self.x_max_as_dt = np.float64(self.x_max).astype("datetime64[s]")

    ###########
    # private #
    ###########

    def _find_shortest_string_representation(self, labels=None) -> list[str]:
        """
        This method will find the shortest strings for datetime labels that
        give enough information.
        """
        if labels is None:
            labels = self.labels
        if self.timezone is not None:
            return self._local_strings(labels)
        # By default, use NumPy's rendering functionality
        short_labels = [str(x) for x in np.datetime_as_string(labels, unit="auto")]
        # Remove the date if it is the same in all labels
        if len(set(np.datetime_as_string(labels, unit="D"))) == 1:
            # The "auto" unit renders midnight as a date only
            short_labels = [t[11:] or "00:00" for t in short_labels]
        # Remove day, and then month, if that is redundant (i.e. all labels
        # have a "-01" at the end)
        for _ in range(2):
            if all(re.fullmatch(r"[\d-]+-01", s) for s in short_labels):
                short_labels = [t[:-3] for t in short_labels]
            else:
                break

        return short_labels

    def _local_strings(self, labels: NDArray) -> list[str]:
        assert self.timezone is not None
        local = utc_to_local(labels, self.timezone)
        bounds = utc_to_local(
            np.array([self.x_min_as_dt, self.x_max_as_dt]), self.timezone
        )
        same_day = bounds[0].astype("datetime64[D]") == bounds[1].astype(
            "datetime64[D]"
        )
        same_year = bounds[0].astype("datetime64[Y]") == bounds[1].astype(
            "datetime64[Y]"
        )
        strings = [str(x) for x in np.datetime_as_string(local, unit="auto")]
        all_midnight = all(len(value) == 10 for value in strings)
        if same_day:
            strings = [value[11:] or "00:00" for value in strings]
        elif not all_midnight:
            # Each tick carries its own date. Never infer date redundancy from
            # selected ticks alone: the viewport may also include the day before.
            strings = [
                (value[5:10] if same_year else value[:10])
                + " "
                + (value[11:] or "00:00")
                for value in strings
            ]
        else:
            for _ in range(2):
                if all(re.fullmatch(r"[\d-]+-01", value) for value in strings):
                    strings = [value[:-3] for value in strings]
                else:
                    break
        for i, wall_time in enumerate(local.astype(int)):
            if len(local_to_utc_seconds(int(wall_time), self.timezone)) > 1:
                instant = datetime.fromtimestamp(
                    float(labels[i].astype(float)), self.timezone
                )
                offset = instant.strftime("%z")
                offset = (
                    offset[:3]
                    + ":"
                    + offset[3:5]
                    + (":" + offset[5:] if len(offset) > 5 else "")
                )
                strings[i] += offset
        return strings

    def _spread_greater_than(self, count: int, unit: str) -> bool:
        x = np.timedelta64(count, unit).astype("<m8[s]")  # type: ignore
        return (self.x_max_as_dt - self.x_min_as_dt).astype("<m8[s]") > x
