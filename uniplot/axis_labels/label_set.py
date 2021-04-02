import numpy as np  # type: ignore
from typing import List, Optional

from uniplot.discretizer import discretize


class LabelSet:
    def __init__(
        self,
        labels: np.array,
        x_min: float,
        x_max: float,
        available_space: int,
        vertical_direction: bool = False,
    ):
        self.labels = labels
        self.x_min = x_min
        self.x_max = x_max
        self.available_space = available_space
        self.vertical_direction = vertical_direction

    def to_string(self) -> str:
        str_labels = self._find_shortest_string_representation(self.labels)
        line = ""
        for i, label in enumerate(self.labels):
            str_label = str_labels[i]
            offset = max(
                0,
                discretize(
                    label,
                    x_min=self.x_min,
                    x_max=self.x_max,
                    steps=self.available_space,
                )
                - int(0.5 * len(str_label)),
            )
            buffer = offset - len(line)
            if i > 0 and buffer < 1:
                # TODO Fix this
                raise

            line = line + (" " * buffer) + str_label

        return line

    ###########
    # private #
    ###########

    def _find_shortest_string_representation(
        self,
        numbers: List[Optional[float]],
    ) -> List[str]:
        """
        This method will find the shortest numerical values for axis labels that are different from ech other.
        """
        compact_abs_numbers = [abs(n) for n in numbers if n is not None]

        # We actually want to add one more digit than needed for uniqueness
        for nr_digits in range(10):
            # The test for the right number of digits happens on the absolute numbers. See issue #5.
            test_list = [self._float_format(n, nr_digits) for n in compact_abs_numbers]
            if len(test_list) == len(set(test_list)):
                return [
                    "" if n is None else self._float_format(n, nr_digits)
                    for n in numbers
                ]

        # Fallback to naive string conversion
        return ["" if n is None else str(n) for n in numbers]

    def _float_format(self, n: float, nr_digits: int):
        if nr_digits == 0:
            return ("{:,d}").format(int(n))
        return ("{:,." + str(nr_digits) + "f}").format(float(n))
