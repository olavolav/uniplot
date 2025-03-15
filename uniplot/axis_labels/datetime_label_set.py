import re
import numpy as np
from numpy.typing import NDArray
from typing import List

from uniplot.axis_labels.label_set import LabelSet


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
    ):
        super().__init__(
            labels, x_min, x_max, available_space, unit, log, vertical_direction
        )
        # For convenience, make sure we have the bounds also available as
        # datetime objects.
        self.x_min_as_dt = np.float64(self.x_min).astype("datetime64[s]")
        self.x_max_as_dt = np.float64(self.x_max).astype("datetime64[s]")

    ###########
    # private #
    ###########

    def _find_shortest_string_representation(self) -> List[str]:
        """
        This method will find the shortest strings for datetime labels that
        give enough information.
        """
        # By default, use NumPy's redering functionality
        short_labels = list(np.datetime_as_string(self.labels, unit="auto"))
        # Remove the date if it is the same in all labels
        if len(set(np.datetime_as_string(self.labels, unit="D"))) == 1:
            short_labels = [t[11:] for t in short_labels]
        # Remove day, and then month, if that is redundant (i.e. all labels
        # have a "-01" at the end)
        for _ in range(2):
            if all([re.fullmatch(r"[\d-]+-01", s) for s in short_labels]):
                short_labels = [t[:-3] for t in short_labels]
            else:
                break

        return short_labels

    def _spread_greater_than(self, count: int, unit: str) -> bool:
        x = np.timedelta64(count, unit).astype("<m8[s]")
        return (self.x_max_as_dt - self.x_min_as_dt).astype("<m8[s]") > x
