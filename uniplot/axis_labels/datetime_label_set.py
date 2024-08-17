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

    def _post_process_init(self) -> None:
        """
        For convenience, make sure we have the bounds also available as datetime objects.
        """
        self.x_min_as_dt = np.float64(self.x_min).astype("datetime64[s]")
        self.x_max_as_dt = np.float64(self.x_max).astype("datetime64[s]")

    def _find_shortest_string_representation(
        self,
        numbers: NDArray,
    ) -> List[str]:
        """
        This method will find the shortest strings for datetime labels that give enough information.

        Note: The implementation here is only a starting point.
        """
        test_list: List[str] = []
        # for unit in NICE_DATETIME_UNITS:
        #     if self._spread_greater_than(10, unit):
        #         # Found the right level
        #         test_list = list(np.datetime_as_string(numbers, unit=unit))  # type: ignore
        #         break

        # Fallback
        if len(test_list) < 1:
            test_list = list(np.datetime_as_string(numbers, unit="auto"))
        # Remove the date if it is the same in all labels
        if len(set(np.datetime_as_string(numbers, unit="D"))) == 1:
            test_list = [t[11:] for t in test_list]

        return test_list

    def _spread_greater_than(self, count: int, unit: str) -> bool:
        x = np.timedelta64(count, unit).astype("<m8[s]")
        return (self.x_max_as_dt - self.x_min_as_dt).astype("<m8[s]") > x
