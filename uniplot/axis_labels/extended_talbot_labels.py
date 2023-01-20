import numpy as np  # type: ignore
from typing import Optional

from uniplot.axis_labels.label_set import LabelSet

# Preference-ordered list of "nice" numbers
Q_VALUES = [1, 5, 2, 2.5, 4, 3]
# Weights to be able to combine the different scores
WEIGHTS = np.array([0.4, 0.25, 0.3, 0.2])
# The "depth" of the search
MAX_SKIP_AMOUNT = 9


def extended_talbot_labels(
    x_min: float,
    x_max: float,
    available_space: int,
    vertical_direction: bool = False,
    unit: str = "",
    log: bool = False,
    verbose: bool = False,
) -> Optional[LabelSet]:
    """
    The following is based on the paper Talbot, J., Lin, S. & Hanrahan, P. An Extension of Wilkinson’s Algorithm for Positioning Tick Labels on Axes. IEEE T Vis Comput Gr 16, 1036–1043 (2010).
    We have further exteded the algorithm to account for the discrete nature of terminal output.
    """
    result: Optional[LabelSet] = None
    best_score: float = -2.0

    data_range: float = x_max - x_min
    base_exponent = int(np.log10(data_range))

    preferred_nr_labels = _compute_preferred_number_of_labels(
        available_space, vertical_direction
    )

    for exponent in [base_exponent, base_exponent - 1]:
        # Find closest "zero" and thus the start of the label generation
        f = x_min / 10 ** (exponent + 1)
        label_start = np.floor(f) * 10 ** (exponent + 1)

        # j is the "skip amount"
        for j in range(1, MAX_SKIP_AMOUNT + 1):
            # i is the index of the currently selected "nice" number q
            for i, q in enumerate(Q_VALUES):
                step_size = q * j

                labels = np.arange(
                    start=label_start,
                    stop=x_max,
                    step=step_size * 10**exponent,
                )
                # Crop labels
                labels = labels[(labels >= x_min) & (labels <= x_max)]
                if len(labels) < 2:
                    continue

                simplicity = _compute_simplicity_score(labels, i, j)
                coverage = _compute_coverage_score(labels, x_min, x_max)
                density = _compute_density_score(labels, preferred_nr_labels)

                # Performance improvement
                score_approx = np.dot(
                    np.array([simplicity, coverage, density, 1]), WEIGHTS
                )
                if (result is not None) and (score_approx < best_score):
                    continue

                # Generate `LabelSet` instance to compute remaining scores
                current_set = LabelSet(
                    labels,
                    x_min=x_min,
                    x_max=x_max,
                    available_space=available_space,
                    unit=unit,
                    log=log,
                    vertical_direction=vertical_direction,
                )

                # TODO Simplistic grid alignment score is used, needs refinement
                grid_alignment = 1 - 100 * int(
                    current_set.compute_if_render_does_overlap()
                )
                score = np.dot(
                    np.array([simplicity, coverage, density, grid_alignment]),
                    WEIGHTS,
                )
                if verbose:
                    print(
                        f"Testing labels: {labels} => simplicity = {simplicity}, coverage = {coverage}, density = {density}, grid_alignment => {grid_alignment}, score = {score}"
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


def _compute_preferred_number_of_labels(
    available_space: int, vertical_direction: bool
) -> int:
    """
    Compute an estimate for the preferred number of labels.
    """
    # For horizontal direction (x axis)
    preferred_number_of_labels = int(available_space / 15)

    if vertical_direction:
        # for y axis
        preferred_number_of_labels = int(available_space / 5.6)

    return max(2, min(20, preferred_number_of_labels))


def _compute_simplicity_score(labels, i: int, j: int) -> float:
    """
    Simplicity score according to Talbot.
    """
    # Indicator variable that is one if zero is part of the labels, and zero otherwise
    # NOTE It might make sense to extend this to all gridline values, plus zero
    v = int(0.0 in labels)
    return 1 - (i - 1) / (len(Q_VALUES) - 1) - j + v


def _compute_coverage_score(labels, x_min: float, x_max: float) -> float:
    """
    Coverage score according to Talbot.
    """
    return 1 - 5 * ((x_max - labels[-1]) ** 2 + (x_min - labels[0]) ** 2) / (
        (x_max - x_min) ** 2
    )


def _compute_density_score(labels, preferred_nr: int) -> float:
    """
    Density score according to Talbot.
    """
    return 1 - max(len(labels) / preferred_nr, preferred_nr / len(labels))
