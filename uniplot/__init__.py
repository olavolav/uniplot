# Add a shortcut such that users of the library can write `from uniplot import plot`
# instead of `from uniplot.uniplot import plot`.
from uniplot.uniplot import plot, plot_to_string, histogram
from uniplot.options import Widget

__all__ = ["plot", "plot_to_string", "histogram", "Widget"]
