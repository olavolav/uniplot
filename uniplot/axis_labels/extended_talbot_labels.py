import numpy as np  # type: ignore
from typing import List, Optional

# Preference-ordered list of "nice" numbers
Q_VALUES = [1, 5, 2, 2.5, 4, 3]
# Weights to be able to combine the different scores
WEIGHTS = np.array([0.2, 0.25, 0.5, 0.05])


def extended_talbot_labels(
    x_min: float, x_max: float, available_space: int, vertical_direction: bool = False
) -> Optional[float]:
    result: Optional[np.array] = None
    best_score: float = -2.0

    data_range: float = x_max - x_min
    base_exponent = int(np.log10(data_range))

    # Set the preferred number of labels
    preferred_number_of_labels = int(available_space / 2)
    if vertical_direction is False:
        preferred_number_of_labels = int(available_space / 15)

    for exponent in [base_exponent, base_exponent - 1]:
        x_min_normalized = int(np.floor(x_min / 10 ** exponent))
        x_max_normalized = int(np.ceil(x_max / 10 ** exponent))
        print(
            f"DEBUG: exponent = {exponent}, x_min_normalized = {x_min_normalized}, x_max_normalized = {x_max_normalized}"
        )

        # j is the "skip amount"
        for j in range(1, 10):
            # i is the index of the currently selected "nice" number q
            for i, q in enumerate(Q_VALUES):
                q = Q_VALUES[i]
                single_step_size = q / (10 ** int(np.log10(j * q)))
                step_size = j * single_step_size
                print(f"DEBUG: j = {j}, q = {q}, step_size = {step_size}")

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

                    if len(labels) < 2:
                        # print("Invalid, skipping ...")
                        continue

                    simplicity = _compute_simplicity_score(labels, i, j)
                    coverage = _compute_coverage_score(labels, x_min, x_max)
                    density = _compute_density_score(labels, preferred_number_of_labels)
                    score = np.dot(
                        np.array([simplicity, coverage, density, 1]), WEIGHTS
                    )

                    # if np.dot(np.array([s, 1, 1, 1]), WEIGHTS) < best_score:
                    if score > best_score:
                        print(
                            f"DEBUG: simplicity = {simplicity}, coverage = {coverage}, density = {density} => score = {score}"
                        )
                        print(f"DEBUG: New best score 😀 labels = {labels}")
                        best_score = score
                        result = labels

    return result


###########
# private #
###########


def _compute_simplicity_score(labels, i: int, j: int) -> float:
    """
    Simplicity Score according to Talbot.
    """
    # Indicator if zero is part of the labels
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
