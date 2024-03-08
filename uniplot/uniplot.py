import numpy as np
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
    loop_iteration: int = 0
    while True:
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

            if key_pressed in ["h", "a"]:
                options.shift_view_left()
            elif key_pressed in ["l", "d"]:
                options.shift_view_right()
            elif key_pressed in ["j", "x"]:
                options.shift_view_down()
            elif key_pressed in ["k", "e"]:
                options.shift_view_up()
            elif key_pressed in ["u", "w"]:
                options.zoom_in()
            elif key_pressed in ["n", "s"]:
                options.zoom_out()
            elif key_pressed == "r":
                options.reset_view()
            elif key_pressed in ["q", "\x1b"]:
                # q and Escape will end interactive mode
                break

            loop_iteration += 1
        else:
            # If not in interactive mode
            break


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

    bins_min = bins_min or multi_series.y_min()
    bins_max = bins_max or multi_series.y_max()
    range = bins_max - bins_min
    if range > 0:
        bins_min = bins_min - 0.1 * range
        bins_max = bins_max + 0.1 * range

    xs_histo_series = []
    ys_histo_series = []
    for s in multi_series.ys:
        hist, bin_edges = np.histogram(s, bins=bins)

        # Draw vertical and horizontal lines to connect points
        xs_here = np.zeros(1 + 2 * bins + 1)
        ys_here = np.zeros(1 + 2 * bins + 1)
        xs_here[0] = bin_edges[0]
        xs_here[1::2] = bin_edges
        xs_here[2::2] = bin_edges[1:]
        ys_here[1:-1:2] = hist
        ys_here[2:-1:2] = hist

        xs_histo_series.append(xs_here)
        ys_histo_series.append(ys_here)

    plot(xs=xs_histo_series, ys=ys_histo_series, **kwargs)
