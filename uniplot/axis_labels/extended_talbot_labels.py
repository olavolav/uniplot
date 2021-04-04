import numpy as np  # type: ignore
from typing import List, Optional

from uniplot.axis_labels.label_set import LabelSet

# Preference-ordered list of "nice" numbers
Q_VALUES = [1, 5, 2, 2.5, 4, 3]
# Weights to be able to combine the different scores
WEIGHTS = np.array([0.2, 0.2, 0.4, 0.2])
# The "depth" of the search
MAX_SKIP_AMOUNT = 9


def extended_talbot_labels(
    x_min: float,
    x_max: float,
    available_space: int,
    vertical_direction: bool = False,
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

    # HACK Set the preferred number of labels
    preferred_number_of_labels = int(available_space / 4)
    if vertical_direction is False:
        preferred_number_of_labels = int(available_space / 15)

    for exponent in [base_exponent, base_exponent - 1]:
        x_min_normalized = int(np.floor(x_min / 10 ** exponent))
        x_max_normalized = int(np.ceil(x_max / 10 ** exponent))

        # j is the "skip amount"
        for j in range(1, MAX_SKIP_AMOUNT + 1):
            # i is the index of the currently selected "nice" number q
            for i, q in enumerate(Q_VALUES):
                q = Q_VALUES[i]
                single_step_size = q / (10 ** int(np.log10(j * q)))
                step_size = j * single_step_size

                for offset in range(j):
                    labels = (
                        np.arange(
                            x_min_normalized + offset,
                            x_max_normalized + 1,
                            step=step_size,
                        )
                        * 10 ** exponent
                    )
                    # Crop labels
                    labels = labels[(labels >= x_min) & (labels <= x_max)]

                    # Skipping is less than two labels
                    if len(labels) < 2:
                        continue

                    simplicity = _compute_simplicity_score(labels, i, j)
                    coverage = _compute_coverage_score(labels, x_min, x_max)
                    density = _compute_density_score(labels, preferred_number_of_labels)

                    # Performance improvement
                    if (
                        result is not None
                        and np.dot(
                            np.array([simplicity, coverage, density, 1]), WEIGHTS
                        )
                        < best_score
                    ):
                        continue

                    # Generate `LabelSet` instance to compute remaining scores
                    current_set = LabelSet(
                        labels,
                        x_min=x_min,
                        x_max=x_max,
                        available_space=available_space,
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

                    if score > best_score:
                        if verbose:
                            print(
                                f"DEBUG: simplicity = {simplicity}, coverage = {coverage}, density = {density}, grid_alignment = {grid_alignment} => New best score 😀 = {score} with labels = {labels}"
                            )
                        best_score = score
                        result = current_set

    return result


###########
# private #
###########


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
