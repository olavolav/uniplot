from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np  # type: ignore


def _default_y_gridlines() -> List[float]:
    return [0.0]


@dataclass
class Options:
    # Minimum x value of the current view
    x_min: float = 0.0
    # Maximun x value of the current view
    x_max: float = 1.0
    # Minimum y value of the current view
    y_min: float = 0.0
    # Maximun y value of the current view
    y_max: float = 1.0
    # Title of the plot
    title: Optional[str] = None
    # Horizontal gridlines
    y_gridlines: List[float] = field(default_factory=_default_y_gridlines)
    # Width of the plotting region, in characters
    width: int = 60
    # Height of the plotting region, in lines
    height: int = 17
    # Interactive mode
    interactive: bool = False

    def initialize_view_to_show_all(self, xs: np.array, ys: np.array) -> None:
        self.x_min = xs.min()
        self.x_max = xs.max()
        self.y_min = ys.min()
        self.y_max = ys.max()

        # Remeber values for resetting later
        self._initial_bounds = (self.x_min, self.x_max, self.y_min, self.y_max)

    def reset_view(self) -> None:
        (self.x_min, self.x_max, self.y_min, self.y_max) = self._initial_bounds
