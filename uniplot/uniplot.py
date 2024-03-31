from typing import List, Optional, Any

from uniplot.multi_series import MultiSeries
from uniplot.options import Options
from uniplot.param_initializer import validate_and_transform_options
import uniplot.sections as sections
import uniplot.plot_elements as elements
from uniplot.getch import getch


def plot(ys: Any, xs: Optional[Any] = None, **kwargs) -> None:
    """
    2D scatter dot plot on the terminal.

    Parameters:

    - `ys` are the y coordinates of the points to plot. This parameter is
      mandatory and can either be a list or a list of lists, or the equivalent
      NumPy array.
    - `xs` are the x coordinates of the points to plot. This parameter is
      optional and can either be a `None` or of the same shape as `ys`.
    - Any additional keyword arguments are passed to the
      `uniplot.options.Options` class.
    """
    series: MultiSeries = MultiSeries(xs=xs, ys=ys)
    options: Options = validate_and_transform_options(series=series, kwargs=kwargs)

    # Print header
    for line in sections.generate_header(options):
        print(line)

    # Main loop for interactive mode. Will only be executed once when not in
    # interactive mode.
    continue_looping: bool = True
    loop_iteration: int = 0
    while continue_looping:
        # Make sure we stop after first iteration when not in interactive mode
        if not options.interactive:
            continue_looping = False

        (
            x_axis_labels,
            y_axis_labels,
            pixel_character_matrix,
        ) = sections.generate_body_raw_elements(series, options)

        # Delete plot before we re-draw
        if loop_iteration > 0:
            nr_lines_to_erase = options.height + 4
            if options.legend_labels is not None:
                nr_lines_to_erase += len(options.legend_labels)
            elements.erase_previous_lines(nr_lines_to_erase)

        for line in sections.generate_body(
            x_axis_labels, y_axis_labels, pixel_character_matrix, options
        ):
            print(line)

        if options.interactive:
            print("Move h/j/k/l, zoom u/n, or r to reset. ESC/q to quit")
            key_pressed = getch().lower()

            if key_pressed == "h":
                options.shift_view_left()
            elif key_pressed == "l":
                options.shift_view_right()
            elif key_pressed == "j":
                options.shift_view_down()
            elif key_pressed == "k":
                options.shift_view_up()
            elif key_pressed == "u":
                options.zoom_in()
            elif key_pressed == "n":
                options.zoom_out()
            elif key_pressed == "r":
                options.reset_view()
            elif key_pressed in ["q", "\x1b"]:
                # q and Escape will end interactive mode
                continue_looping = False
            else:
                options.dispatch(key_pressed)

            loop_iteration += 1


def plot_to_string(ys: Any, xs: Optional[Any] = None, **kwargs) -> List[str]:
    """
    Same as `plot`, but the return type is a list of strings. Ignores the
    `interactive` option.

    Can be used to integrate uniplot in other applications, or if the output is
    desired to be not stdout.
    """
    series: MultiSeries = MultiSeries(xs=xs, ys=ys)
    options: Options = validate_and_transform_options(series=series, kwargs=kwargs)

    header = sections.generate_header(options)
    (
        x_axis_labels,
        y_axis_labels,
        pixel_character_matrix,
    ) = sections.generate_body_raw_elements(series, options)

    body = sections.generate_body(
        x_axis_labels, y_axis_labels, pixel_character_matrix, options
    )
    return header + body


#####################################
# Experimental features, see Readme #
#####################################


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
    # HACK Use the `MultiSeries` constructor to cast values to uniform format
    multi_series = MultiSeries(ys=xs)

    # Histograms usually make sense only with lines
    kwargs["lines"] = kwargs.get("lines", True)

    bins_min_real: float = bins_min or multi_series.y_min()
    bins_max_real: float = bins_max or multi_series.y_max()
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

    plot(xs=xs_histo_series, ys=ys_histo_series, **kwargs)
