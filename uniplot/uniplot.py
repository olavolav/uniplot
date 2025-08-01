from typing import List, Dict, Optional, Final, Any
from readchar import readkey, key

from uniplot.multi_series import MultiSeries
from uniplot.options import Options
from uniplot.param_initializer import validate_and_transform_options
import uniplot.sections as sections
import uniplot.plot_elements as elements


def plot(ys: Any, xs: Optional[Any] = None, **kwargs) -> None:
    """
    2D plot on the terminal.

    Parameters:

    - `ys` are the y coordinates of the points to plot. This parameter is
      mandatory and can either be a list or a list of lists, or the equivalent
      NumPy array.
    - `xs` are the x coordinates of the points to plot. This parameter is
      optional and can either be a `None` or of the same shape as `ys`.
    - Any additional keyword arguments are passed to the
      `uniplot.options.Options` class.
    """
    plt = plot_gen(xs=xs, ys=ys, **kwargs)

    # Main loop for interactive mode. Will only be executed once when not in
    # interactive mode.
    first_iteration: bool = True
    while first_iteration or plt.options.interactive:
        plt.update()

        if plt.options.interactive:
            plt.print_subscript("Move h/j/k/l, zoom u/n, or r to reset. q to quit.")
            key_pressed = readkey()

            # Here we support 3 ways to move: Vim-style, arrow keys and FPS-style
            if key_pressed in ["h", key.LEFT, "a"]:
                plt.options.shift_view_left()
            elif key_pressed in ["l", key.RIGHT, "d"]:
                plt.options.shift_view_right()
            elif key_pressed in ["j", key.DOWN, "s"]:
                plt.options.shift_view_down()
            elif key_pressed in ["k", key.UP, "w"]:
                plt.options.shift_view_up()
            elif key_pressed in ["u", "]"]:
                plt.options.zoom_in()
            elif key_pressed in ["n", "["]:
                plt.options.zoom_out()
            elif key_pressed == "r":
                plt.options.reset_view()
            elif key_pressed in ["q", "Q", key.ESC]:
                break

        first_iteration = False


class plot_gen:
    def __init__(self, return_string=False, **kwargs) -> None:
        self.default_arguments: Final[Dict] = kwargs
        self.last_nr_of_lines: int = 0
        self.return_string: Final[bool] = return_string
        self.series: MultiSeries = MultiSeries([])
        self.options: Options = Options()
        if "ys" in kwargs:
            self.series = MultiSeries(xs=kwargs.get("xs"), ys=kwargs.get("ys", []))
            if "xs" in kwargs:
                del kwargs["xs"]
            del kwargs["ys"]
            self.options = validate_and_transform_options(
                series=self.series, kwargs=kwargs
            )

    def update(self, **kwargs) -> Optional[str]:
        header_buffer: List[str] = []
        body_buffer: List[str] = []

        full_kwargs = {**self.default_arguments, **kwargs}

        if "xs" in kwargs or "ys" in kwargs:
            self.series = MultiSeries(
                xs=full_kwargs.get("xs"), ys=full_kwargs.get("ys")
            )
        if len(kwargs.keys()) > 0 or self.options is None:
            # New options provided, so regenerate `self.options`
            # NOTE This overwrites the view window if not supplied explicitely
            if "xs" in full_kwargs:
                del full_kwargs["xs"]
            del full_kwargs["ys"]
            self.options = validate_and_transform_options(
                series=self.series, kwargs=full_kwargs
            )

        header_buffer = sections.generate_header(self.options)

        # Generate and collect plot content
        body_buffer = []
        (
            x_axis_labels,
            y_axis_labels,
            pixel_character_matrix,
        ) = sections.generate_body_raw_elements(self.series, self.options)
        body_buffer += sections.generate_body(
            x_axis_labels, y_axis_labels, pixel_character_matrix, self.options
        )

        # Delete plot before we re-draw
        if not self.return_string:
            elements.erase_previous_lines(self.last_nr_of_lines)

        # Output plot
        output = "\n".join(header_buffer + body_buffer)
        self.last_nr_of_lines = elements.count_lines(output)
        if self.return_string:
            return output
        print(output)
        return None

    def print_subscript(self, text: str) -> None:
        self.last_nr_of_lines += elements.count_lines(text)
        print(text)


def plot_to_string(ys: Any, xs: Optional[Any] = None, **kwargs) -> str:
    """
    Same as `plot`, but the return type is string. Ignores the `interactive`
    option.

    Can be used to integrate uniplot in other applications, or if the output is
    desired to be not stdout.
    """
    plt = plot_gen(return_string=True)
    return str(plt.update(xs=xs, ys=ys, **kwargs))


#####################################
# Experimental features, see Readme #
#####################################


def prepare_histogram(
    xs: Any,
    bins: int = 20,
    bins_min: Optional[float] = None,
    bins_max: Optional[float] = None,
    **kwargs,
):
    # HACK Use the `MultiSeries` constructor to cast values to uniform format
    multi_series = MultiSeries(ys=xs)

    # Histograms usually make sense only with lines
    kwargs["lines"] = kwargs.get("lines", True)

    bins_min_real: float = bins_min if bins_min is not None else multi_series.y_min()
    bins_max_real: float = bins_max if bins_max is not None else multi_series.y_max()
    assert bins_max_real > bins_min_real

    # Depending on whether the bin limits were supplied as arguments, expand
    # the width automatically
    delta: float = bins_max_real - bins_min_real
    if bins_min is None:
        bins_min_real = bins_min_real - 0.1 * delta
    if bins_max is None:
        bins_max_real = bins_max_real + 0.1 * delta

    # Compute bin edges
    bin_edges = [
        bins_min_real + i * (bins_max_real - bins_min_real) / bins
        for i in range(bins + 1)
    ]

    xs_histo_series = []
    ys_histo_series = []
    for s in multi_series.ys:
        xs_barchart, ys_barchart = elements.compute_bar_chart_histogram_points(
            s, bin_edges
        )
        xs_histo_series.append(xs_barchart)
        ys_histo_series.append(ys_barchart)

    return xs_histo_series, ys_histo_series, kwargs


def histogram(
    xs: Any,
    bins: int = 20,
    bins_min: Optional[float] = None,
    bins_max: Optional[float] = None,
    **kwargs,
) -> None:
    """
    Plot a histogram to the terminal.

    Parameters:

    - `xs` are the values of the points to plot. This parameter is mandatory
      and can either be a list or a list of lists, or the equivalent NumPy
      array.
    - Any additional keyword arguments are passed to the
      `uniplot.options.Options` class.
    """
    xs_histo_series, ys_histo_series, kwargs = prepare_histogram(
        xs, bins, bins_min, bins_max, **kwargs
    )
    plot(xs=xs_histo_series, ys=ys_histo_series, **kwargs)


def histogram_to_string(
    xs: Any,
    bins: int = 20,
    bins_min: Optional[float] = None,
    bins_max: Optional[float] = None,
    **kwargs,
) -> str:
    """
    Same as `histogram`, but the return type is string. Ignores the `interactive`
    option.

    Can be used to integrate uniplot in other applications, or if the output is
    desired to be not stdout.
    """
    xs_histo_series, ys_histo_series, kwargs = prepare_histogram(
        xs, bins, bins_min, bins_max, **kwargs
    )
    plt = plot_gen(return_string=True)
    return str(plt.update(xs=xs_histo_series, ys=ys_histo_series, **kwargs))
