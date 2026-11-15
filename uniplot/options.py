from dataclasses import dataclass, field
from typing import Literal

from uniplot.character_sets import ASCII_CHARACTER_SET, CharacterSet
from uniplot.colors import Color
from uniplot.legend_placements import LegendPlacement


def _default_gridlines() -> list[float]:
    return [0.0]


def _default_lines() -> list[bool]:
    return [False]


def _default_ascii_characters() -> list[str]:
    return ASCII_CHARACTER_SET


@dataclass
class Options:
    """
    This object holds the options of this run.

    Implementation note: The minima, maxima and gridlines are all stores as
    `float` values, regardless of the data type that is being plotted.
    """

    # Frame around the plot area
    border: Literal["box", "rounded"] | None = "box"
    # Character set
    character_set: CharacterSet = CharacterSet.BLOCK
    # Color mode
    color: list[Color] | None = None
    # Per-series baseline in plot coordinates, or "bottom" / None
    fill: list[float | str | None] = field(default_factory=lambda: [None])
    # List of characters to use when plotting in force_ascii mode.
    force_ascii_characters: list[str] = field(default_factory=_default_ascii_characters)
    # Height of the plotting region, in lines
    height: int = 17
    # Interactive mode
    interactive: bool = False
    # Labels for the series
    legend_labels: list[str] | None = None
    # Legend placement
    legend_placement: LegendPlacement = LegendPlacement.AUTO
    # Enforce a hard limit on the number of characters per line. This may
    # override the `width` option if there is not enough space.
    line_length_hard_cap: int | None = None
    # Draw lines between points
    lines: list[bool] = field(default_factory=_default_lines)
    # Deprecated rounded corners option. Remove no earlier than 2027-05-14.
    rounded_corners: bool = False
    # Title of the plot
    title: str | None = None
    # Width of the plotting region, in characters
    width: int = 60
    # Plot x axis with log scale
    x_as_log: bool = False
    # Vertical gridlines
    x_gridlines: list[float] = field(default_factory=_default_gridlines)
    # Color of vertical gridlines
    x_gridlines_color: list[Color] | None = None
    # Enable x axis labels
    x_labels: bool = True
    # Maximum x value of the current view
    x_max: float = 1.0
    # Minimum x value of the current view
    x_min: float = 0.0
    # Units of x axis
    x_unit: str = ""
    # Scale x axis labels, assuming `x_unit` is the base unit. Supported values:
    # "" (no scaling) and "si" (SI prefixes: k, M, G, … and m, µ, n, …; e.g.
    # with `x_unit=" m"` a label of 1,000 renders as "1 km"). The prefix is
    # inserted before the first non-whitespace character of the unit, so a
    # leading space is preserved; a blank `x_unit` still gets a prefix ("200k").
    x_unit_scaling: str = ""
    # Plot y axis with log scale
    y_as_log: bool = False
    # Horizontal gridlines
    y_gridlines: list[float] = field(default_factory=_default_gridlines)
    # Color of horizontal gridlines
    y_gridlines_color: list[Color] | None = None
    # Enable y axis labels
    y_labels: bool = True
    # Maximum y value of the current view
    y_max: float = 1.0
    # Minimum y value of the current view
    y_min: float = 0.0
    # Units of y axis
    y_unit: str = ""
    # Scale y axis labels, assuming `y_unit` is the base unit. See
    # `x_unit_scaling`. Supported values: "" (no scaling) and "si".
    y_unit_scaling: str = ""

    def __post_init__(self):
        # Validate values
        assert self.width > 0
        assert self.height > 0
        if self.border not in ("box", "rounded", None):
            raise ValueError('border must be "box", "rounded", or None.')
        if self.border == "box" and self.rounded_corners:
            self.border = "rounded"

        # Remember values for resetting later
        self._initial_bounds = (self.x_min, self.x_max, self.y_min, self.y_max)
        self._initial_width = self.width

    def shift_view_left(self) -> None:
        self.__shift_view_horizontal(factor=-1)

    def shift_view_right(self) -> None:
        self.__shift_view_horizontal(factor=1)

    def shift_view_up(self) -> None:
        self.__shift_view_vertical(factor=1)

    def shift_view_down(self) -> None:
        self.__shift_view_vertical(factor=-1)

    def zoom_in(self) -> None:
        self.__zoom_view(factor=1)

    def zoom_out(self) -> None:
        self.__zoom_view(factor=-1)

    def reset_view(self) -> None:
        (self.x_min, self.x_max, self.y_min, self.y_max) = self._initial_bounds

    def reset_width(self) -> None:
        self.width = self._initial_width

    ###########
    # private #
    ###########

    def __shift_view_horizontal(self, factor: int) -> None:
        # TODO Make the step aligned with the characters on the screen
        step: float = 0.1 * factor * (self.x_max - self.x_min)
        self.x_min = self.x_min + step
        self.x_max = self.x_max + step

    def __shift_view_vertical(self, factor: int) -> None:
        # TODO Make the step aligned with the characters on the screen
        step: float = 0.1 * factor * (self.y_max - self.y_min)
        self.y_min = self.y_min + step
        self.y_max = self.y_max + step

    def __zoom_view(self, factor: int) -> None:
        step: float = 0.1 * factor * (self.x_max - self.x_min)
        self.x_min = self.x_min + step
        self.x_max = self.x_max - step

        step = 0.1 * factor * (self.y_max - self.y_min)
        self.y_min = self.y_min + step
        self.y_max = self.y_max - step
