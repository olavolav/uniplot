import numpy as np
from numpy.typing import NDArray

from uniplot.discretizer import discretize, discretize_array

LEFT_MARGIN_FOR_HORIZONTAL_AXIS = 1


def _max_length(labels: list[str]) -> int:
    return max((len(label) for label in labels), default=0)


# SI prefixes indexed by the power-of-1000 group, e.g. group 1 => "k" (10^3),
# group -1 => "m" (10^-3). Group 0 is the base unit and has no prefix.
SI_PREFIXES = {
    -8: "y",  # yocto
    -7: "z",  # zepto
    -6: "a",  # atto
    -5: "f",  # femto
    -4: "p",  # pico
    -3: "n",  # nano
    -2: "µ",  # micro
    -1: "m",  # milli
    0: "",
    1: "k",  # kilo
    2: "M",  # mega
    3: "G",  # giga
    4: "T",  # tera
    5: "P",  # peta
    6: "E",  # exa
    7: "Z",  # zetta
    8: "Y",  # yotta
}

# Supported values of the `unit_scaling` option. "" disables scaling; "si" uses
# SI prefixes (see `SI_PREFIXES`). More modes may be added in the future (see
# `plans/unit-scaling-modes.md`).
VALID_UNIT_SCALINGS = frozenset({"", "si"})


class LabelSet:
    """
    This class represents a list of possible axis labels. It can render them to
    a string, or list of strings. It also provides metrics about the rendering
    result.
    """

    def __init__(
        self,
        labels: NDArray,
        x_min: float = 0.0,
        x_max: float = 1.0,
        available_space: int = 17,
        unit: str = "",
        unit_scaling: str = "",
        log: bool = False,
        vertical_direction: bool = False,
        left_margin: int = LEFT_MARGIN_FOR_HORIZONTAL_AXIS,
    ):
        self.labels: NDArray = labels
        self.x_min = x_min
        self.x_max = x_max
        self.unit = unit
        self.unit_scaling = unit_scaling
        self.log = log
        self.available_space = available_space
        self.vertical_direction = vertical_direction
        self.left_margin = left_margin
        self._results_already_in_cache: bool = False
        self._rendered_result: list[str] = []
        self._render_does_overlap: bool = False
        self._spacing_is_regular: bool = True

    def render(self) -> list[str]:
        self._render_and_measure_to_cache()
        return self._rendered_result

    def compute_if_render_does_overlap(self) -> bool:
        self._render_and_measure_to_cache()
        return self._render_does_overlap

    def compute_if_spacing_is_regular(self) -> bool:
        self._render_and_measure_to_cache()
        return self._spacing_is_regular

    ###########
    # private #
    ###########

    def _post_process_init(self) -> None:
        pass

    def _render_and_measure_to_cache(self) -> None:
        # Break if result is already in cache
        if self._results_already_in_cache:
            return

        # Final label strings, including the (optionally SI-prefixed) unit.
        str_labels = self._compute_label_strings()

        if self.vertical_direction:
            # So this is for the y axis case
            lines: list[str] = [""] * self.available_space

            indices = (
                self.available_space
                - 1
                - np.minimum(
                    np.maximum(
                        0,
                        discretize_array(
                            self.labels,
                            x_min=self.x_min,
                            x_max=self.x_max,
                            steps=self.available_space,
                        ),
                    ),
                    self.available_space - 1,
                )
            )
            # This is only done for the vertical direction. For horizontal labels,
            # regular spacing seems not noticable.
            self._spacing_is_regular = self._compute_spacing_of_indices_is_regular(
                indices
            )

            for i, str_label in enumerate(str_labels):
                full_label = str_label
                index = indices[i]
                if lines[index] != "":
                    # This is bad and leads to wrong offsets
                    self._render_does_overlap = True
                lines[index] = full_label

            self._rendered_result = lines
        else:
            # So this is for the x axis case
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
                    - int(0.5 * len(str_label))
                    + self.left_margin,
                )
                buffer = offset - len(line)
                if i == 0 and buffer < 0:
                    # This is bad and leads to wrong offsets
                    buffer = 0
                    self._render_does_overlap = True
                elif i > 0 and buffer < 1:
                    # This is bad and leads to wrong offsets
                    buffer = 1
                    self._render_does_overlap = True

                # Compose string for this line
                line = line + (" " * buffer) + str_label

            self._rendered_result = [line]
        self._results_already_in_cache = True

    def _compute_label_strings(self) -> list[str]:
        """
        Compute the final label strings, including units.

        For linear axes a single SI prefix is chosen for the whole axis, so the
        labels stay visually consistent (e.g. "1km", "2km", "3km"). For log
        axes, where the labels typically span several orders of magnitude, each
        label is instead formatted independently with its own SI prefix.
        """
        if self.log:
            # On a log axis the stored labels are exponents; convert them back
            # to the actual values and format each one on its own.
            return [self._format_value_si(10.0**exponent) for exponent in self.labels]

        base_labels = self._render_linear_labels(divisor=1.0, prefix="")
        divisor, prefix = self._si_divisor_and_prefix()
        if prefix == "":
            return base_labels

        # Only apply the SI prefix if it does not make the labels longer than
        # the plain representation. This keeps values like 0.5 as "0.5 °C"
        # rather than rewriting them as "500 m°C", while still shortening e.g.
        # 0.003 to "3 mm" and 5000 to "5 km".
        prefixed_labels = self._render_linear_labels(divisor, prefix)
        if _max_length(prefixed_labels) <= _max_length(base_labels):
            return prefixed_labels
        return base_labels

    def _render_linear_labels(self, divisor: float, prefix: str) -> list[str]:
        """Render the (non-log) labels for a given SI divisor and prefix."""
        unit = self._apply_si_prefix(prefix, self.unit)
        display_labels = self.labels if divisor == 1.0 else self.labels / divisor
        base_labels = self._find_shortest_string_representation(display_labels)
        return [b + unit for b in base_labels]

    def _find_shortest_string_representation(self, labels=None) -> list[str]:
        """
        This method will find the shortest numerical values for axis labels
        that are different from each other.
        """
        if labels is None:
            labels = self.labels
        # We actually want to add one more digit than needed for uniqueness
        for nr_digits in range(10):
            test_list = [
                self._float_format(n, nr_digits) for n in labels if n is not None
            ]
            if len(test_list) == len(set(test_list)):
                return [
                    "" if n is None else self._float_format(n, nr_digits)
                    for n in labels
                ]

        # Fallback to naive string conversion
        return ["" if n is None else str(n) for n in labels]

    def _si_divisor_and_prefix(self) -> tuple:
        """
        Pick a single SI prefix for the whole (linear) axis and return the
        matching divisor and prefix string. Returns ``(1.0, "")`` when SI
        formatting is disabled, all labels are zero, or the magnitude is beyond
        the range of known prefixes.

        The prefix is anchored to the *smallest* nonzero label, i.e. we pick
        the largest prefix such that no label drops below 1 in the chosen unit.
        This keeps e.g. ``[250, 500, 1000]`` in grams ("250g … 1000g") rather
        than tipping into kilograms with fractional labels ("0.25kg … 1kg").

        A blank unit is allowed: SI prefixes are still applied, so e.g. a value
        of 200,000 renders as "200k".
        """
        if self.unit_scaling != "si":
            return 1.0, ""

        finite = self.labels[np.isfinite(self.labels.astype(float))]
        nonzero = np.abs(finite[finite != 0.0])
        if len(nonzero) == 0:
            return 1.0, ""

        group = self._si_group(float(np.min(nonzero)))
        if group not in SI_PREFIXES:
            # Beyond the range of known prefixes (below yocto or above yotta);
            # fall back to plain formatting without a prefix.
            return 1.0, ""
        return 10.0 ** (3 * group), SI_PREFIXES[group]

    def _si_group(self, value: float) -> int:
        """
        Power-of-1000 group for a value. `floor` division keeps e.g. 999 in the
        base group (999) rather than rounding up into the "k" group. The result
        may fall outside the range of known prefixes (``SI_PREFIXES``), in which
        case callers fall back to plain, prefix-less formatting.
        """
        if value == 0.0:
            return 0
        return int(np.floor(np.log10(abs(value)))) // 3

    def _apply_si_prefix(self, prefix: str, unit: str) -> str:
        """
        Insert the SI prefix directly before the first non-whitespace character
        of the unit, so that a unit of " m" becomes " km" (not "k m") and a
        blank unit becomes just the prefix ("k"). An empty prefix leaves the
        unit unchanged.
        """
        stripped = unit.lstrip()
        leading_whitespace = unit[: len(unit) - len(stripped)]
        return leading_whitespace + prefix + stripped

    def _float_format(self, n: float, nr_digits: int) -> str:
        """
        Format a number to a specified precision.

        Ref.: https://docs.python.org/3.8/library/string.html#format-specification-mini-language
        """
        if nr_digits == 0:
            return f"{round(n):,d}"
        return ("{:,." + str(nr_digits) + "f}").format(float(n))

    def _format_value_si(self, value: float) -> str:
        """
        Format a single value, prepending an SI prefix to the unit when SI
        formatting is enabled. Used for log axes, where each label is scaled
        independently because the labels span several orders of magnitude.
        """
        prefix = ""
        scaled = value
        if self.unit_scaling == "si":
            group = self._si_group(value)
            # Skip the prefix if the value is beyond the known range (below
            # yocto or above yotta) and fall back to plain formatting.
            if group in SI_PREFIXES:
                prefix = SI_PREFIXES[group]
                scaled = value / 10.0 ** (3 * group)
        return self._format_significant(scaled) + self._apply_si_prefix(
            prefix, self.unit
        )

    def _format_significant(self, n: float, significant_digits: int = 3) -> str:
        """
        Format a number to roughly the given number of significant digits,
        grouping thousands with commas and stripping trailing zeros.
        """
        if n == 0.0:
            return "0"
        nr_decimals = significant_digits - 1 - int(np.floor(np.log10(abs(n))))
        nr_decimals = max(0, nr_decimals)
        text = ("{:,." + str(nr_decimals) + "f}").format(float(n))
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text

    def _compute_spacing_of_indices_is_regular(self, indices: NDArray) -> bool:
        return len(np.unique(np.diff(indices))) == 1
