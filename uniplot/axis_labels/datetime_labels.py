import numpy as np
from numpy.typing import NDArray
from typing import Tuple, List, Dict, Optional, Final
from collections import defaultdict
from functools import lru_cache

from uniplot.axis_labels.datetime_label_set import DatetimeLabelSet
from uniplot.axis_labels.extended_talbot_labels import (
    _compute_preferred_number_of_labels,
    _compute_coverage_score,
    _compute_density_score,
)

DIGIT_TIME_UNITS: Final = ["Y", "M", "D", "h", "m", "s"]

# Preference-ordered list of "nice" numbers
Q_VALUES: Final[Dict[str, List]] = defaultdict(
    lambda: [1, 5, 2, 4, 3],
    {
        "M": [1, 4, 3, 2],
        "h": [1, 12, 6, 3, 2],
        "m": [1, 15, 10, 5, 2],
    },
)
# Weights to be able to combine the different scores
WEIGHTS: Final = np.array([0.4, 0.25, 0.3, 0.2])
# The "depth" of the search
MAX_SKIP_AMOUNT: Final = 12


@lru_cache(maxsize=512)
def datetime_labels(
    x_min: float,
    x_max: float,
    available_space: int,
    vertical_direction: bool = False,
    unit: str = "",
    log: bool = False,
    verbose: bool = False,
) -> Optional[DatetimeLabelSet]:
    """
    A simple way to get started with datetime labelling.
    """
    if log:
        # Not supported
        raise

    x_min_as_dt = np.float64(x_min).astype("datetime64[s]")
    x_max_as_dt = np.float64(x_max).astype("datetime64[s]")

    if verbose:
        print(
            f"datetime_labels: x_min={x_min_as_dt}, x_max={x_max_as_dt}, vertical_direction={vertical_direction}"
        )

    result: Optional[DatetimeLabelSet] = None
    best_score: float = -2.0

    data_range = np.timedelta64(x_max_as_dt - x_min_as_dt)
    pseudo_exponent_index, pseudo_exponent = _compute_pseudo_exponent(data_range)
    label_start = _find_left_zero_datetime(x_min_as_dt, pseudo_exponent_index)
    if verbose:
        print(f"pseudo-exponent = {pseudo_exponent}, label_start = {label_start}")

    preferred_nr_labels = _compute_preferred_number_of_labels(
        available_space, vertical_direction
    )

    pseudo_exponents = [pseudo_exponent]
    if pseudo_exponent != "s":
        pseudo_exponents.append(DIGIT_TIME_UNITS[pseudo_exponent_index + 1])
    for pe in pseudo_exponents:
        # j is the "skip amount"
        for j in range(1, MAX_SKIP_AMOUNT + 1):
            # i is the index of the currently selected "nice" number q
            qs = Q_VALUES[pe]
            for i, q in enumerate(qs):
                labels = _label_range(label_start, x_max_as_dt, q * j, pe)

                # Crop labels
                labels = labels[(labels >= x_min_as_dt) & (labels <= x_max_as_dt)]
                if len(labels) < 2:
                    continue

                simplicity = _compute_simplicity_score(qs, i, j)
                coverage = _compute_coverage_score(labels.astype(float), x_min, x_max)
                density = _compute_density_score(labels, preferred_nr_labels)

                score_approx = np.dot(
                    np.array([simplicity, coverage, density, 1]), WEIGHTS
                )
                if (result is not None) and (score_approx < best_score):
                    # The current set cannot be better than the currently best set
                    continue

                # Make labels
                current_set = DatetimeLabelSet(
                    labels=labels,
                    x_min=x_min,
                    x_max=x_max,
                    available_space=available_space,
                    vertical_direction=vertical_direction,
                    unit=unit,
                )

                if current_set.compute_if_render_does_overlap():
                    continue

                grid_alignment = int(current_set.compute_if_spacing_is_regular())

                score = np.dot(
                    np.array([simplicity, coverage, density, grid_alignment]),
                    WEIGHTS,
                )
                if verbose:
                    print(
                        f"Testing labels: {labels}",
                        f" at pe = {pe}, j = {j}, q = {q}",
                        f" => simplicity = {simplicity}, coverage = {coverage},",
                        f" density = {density}, grid_alignment => "
                        f"{grid_alignment}, score = {score}",
                    )
                if score > best_score:
                    if verbose:
                        print("=> New best score 😀")
                    best_score = score
                    result = current_set

    return result


###########
# private #
###########


def _compute_pseudo_exponent(d_range) -> Tuple[int, str]:
    for i, unit in enumerate(DIGIT_TIME_UNITS):
        td = np.timedelta64(1, unit).astype("timedelta64[s]")
        if d_range > td:
            return (i, unit)
    return (len(DIGIT_TIME_UNITS) - 1, DIGIT_TIME_UNITS[-1])


def _find_left_zero_datetime(x_min, unit_index: int):
    one_higher_unit = DIGIT_TIME_UNITS[max(0, unit_index - 1)]
    return x_min.astype(f"datetime64[{one_higher_unit}]").astype("datetime64[s]")


def _label_range(start, stop, step_count: int, step_unit: str) -> NDArray:
    if step_count < 1 or stop < start:
        return np.array([], dtype="datetime64[s]")

    # For units where the step size is an equal amount of seconds
    if step_unit not in ["Y", "M"]:
        step_size = np.timedelta64(step_count, step_unit).astype("timedelta64[s]")
        return np.arange(start=start, stop=stop, step=step_size)

    # Otherwise, manually construct the list
    ls = [start]
    if step_unit == "M":
        step = np.timedelta64(step_count * 31 + 1, "D").astype("timedelta64[s]")
        while True:
            l1 = ls[-1] + step
            l1 = l1.astype("datetime64[M]").astype("datetime64[s]")
            if l1 < stop:
                ls.append(l1)
            else:
                break
        return np.array(ls, dtype="datetime64[s]")

    # Years
    step = np.timedelta64(step_count * 365 + 1, "D").astype("timedelta64[s]")
    while True:
        l1 = ls[-1] + step
        l1 = l1.astype("datetime64[Y]").astype("datetime64[s]")
        if l1 < stop:
            ls.append(l1)
        else:
            break
    return np.array(ls, dtype="datetime64[s]")


def _compute_simplicity_score(q_values, i: int, j: int) -> float:
    """
    Simplicity score according, modified from Talbot.
    """
    return 1 - (i - 1) / (len(q_values) - 1) - j
