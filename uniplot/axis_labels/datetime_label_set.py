import numpy as np
from numpy.typing import NDArray
from typing import List, Final

from uniplot.axis_labels.label_set import LabelSet

DATETIME_PRECISION_LABELS: Final = [
    "Y",
    "M",
    "D",
    "h",
    "m",
    "s",
    "ms",
    "us",
    "ns",
    "ps",
    "fs",
    "as",
]


class DatetimeLabelSet(LabelSet):
    """
    A label set for datetime values like timestamps.
    """

    ###########
    # private #
    ###########

    def _find_shortest_string_representation(
        self,
        numbers: NDArray,
    ) -> List[str]:
        """
        This method will find the shortest strings for axis labels that are different from each other.
        """
        test_list = list(np.datetime_as_string(numbers, unit="auto"))

        if self._spread_greater_than(10, "Y"):
            return list(np.datetime_as_string(numbers, unit="Y"))
        if self._spread_greater_than(10, "D"):
            return list(np.datetime_as_string(numbers, unit="D"))

        # TODO Do this properly, here is just a quick hack to get started
        # Remove the date if it is the same in all labels
        if len(set(np.datetime_as_string(numbers, unit="D"))) == 1:
            return [t[11:] for t in test_list]
        # Once they are all unique, we have found sufficient precision
        return test_list

    def _spread_greater_than(self, count: int, unit: str) -> bool:
        start_date = np.datetime64(int(self.x_min), "s")
        end_date = np.datetime64(int(self.x_max), "s")
        time_span = end_date - start_date
        x = np.timedelta64(count, unit).astype("<m8[s]")
        return time_span > x
