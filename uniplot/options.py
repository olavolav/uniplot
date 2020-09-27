from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np  # type: ignore


def _default_gridlines() -> List[float]:
    return [0.0]


@dataclass
class Options:
    # Color mode
    color: bool = False
    # Height of the plotting region, in lines
    height: int = 17
    # Interactive mode
    interactive: bool = False
    # Labels for the series
    legend_labels: Optional[List[str]] = None
    # Draw lines between points
    lines: bool = False
    # Title of the plot
    title: Optional[str] = None
    # Width of the plotting region, in characters
    width: int = 60
    # Vertical gridlines
    x_gridlines: List[float] = field(default_factory=_default_gridlines)
    # Minimum x value of the current view
    x_min: float = 0.0
    # Maximum x value of the current view
    x_max: float = 1.0
    # Horizontal gridlines
    y_gridlines: List[float] = field(default_factory=_default_gridlines)
    # Minimum y value of the current view
    y_min: float = 0.0
    # Maximum y value of the current view
    y_max: float = 1.0

    def __post_init__(self):
        # Validate values
        assert self.x_max > self.x_min
        assert self.y_max > self.y_min
        assert self.width > 0
        assert self.height > 0

        # Remember values for resetting later
        self._initial_bounds = (self.x_min, self.x_max, self.y_min, self.y_max)

    def reset_view(self) -> None:
        (self.x_min, self.x_max, self.y_min, self.y_max) = self._initial_bounds
