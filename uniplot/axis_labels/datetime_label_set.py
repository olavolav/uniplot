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
        # We actually want to add one more digit than needed for uniqueness
        # for datetime_precision in DATETIME_PRECISION_LABELS:
        # test_list = list(np.datetime_as_string(numbers, unit=datetime_precision))
        test_list = list(np.datetime_as_string(numbers, unit="auto"))

        # TODO Do this properly, here is just a quick hack to get started
        # Remove the date if it is the same in all labels
        if len(set(np.datetime_as_string(numbers, unit="D"))) == 1:
            return [t[11:] for t in test_list]
        # Once they are all unique, we have found sufficient precision
        return test_list
