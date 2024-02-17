import numpy as np
from numpy.typing import NDArray
from typing import List, Final

from uniplot.axis_labels.label_set import LabelSet

NICE_DATETIME_UNITS: Final = [
    "Y",
    "M",
    "D",
    # "h", looks weird
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
        This method will find the shortest strings for datetime labels that give enough information.

        Note: The implementation here is only a starting point.
        """
        for unit in NICE_DATETIME_UNITS:
            if self._spread_greater_than(10, unit):
                return list(np.datetime_as_string(numbers, unit=unit))  # type: ignore
        # Remove the date if it is the same in all labels
        test_list = list(np.datetime_as_string(numbers, unit="auto"))
        if len(set(np.datetime_as_string(numbers, unit="D"))) == 1:
            return [t[11:] for t in test_list]

        return test_list

    def _spread_greater_than(self, count: int, unit: str) -> bool:
        start_date = np.datetime64(int(self.x_min), "s")
        end_date = np.datetime64(int(self.x_max), "s")
        x = np.timedelta64(count, unit).astype("<m8[s]")
        return end_date - start_date > x
