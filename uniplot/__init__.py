# Add a shortcut such that users of the library can write `from uniplot import plot`
# instead of `from uniplot.uniplot import plot`.
from uniplot.uniplot import (
    histogram,
    histogram_to_string,
    plot,
    plot_gen,
    plot_to_string,
    sparkline,
    sparkline_to_string,
)

__all__ = [
    "histogram",
    "histogram_to_string",
    "plot",
    "plot_gen",
    "plot_to_string",
    "sparkline",
    "sparkline_to_string",
]
