import numpy as np
from numpy.typing import NDArray
from typing import Tuple, List, Optional, Any

from uniplot.multi_series import MultiSeries
from uniplot.options import Options
import uniplot.layer_assembly as layer_assembly
import uniplot.plot_elements as elements
from uniplot.getch import getch
from uniplot.param_initializer import validate_and_transform_options
from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels


def plot(ys: Any, xs: Optional[Any] = None, **kwargs) -> None:
    """
    2D scatter dot plot on the terminal.

    Parameters:

    - `ys` are the y coordinates of the points to plot. This parameter is mandatory and
      can either be a list or a list of lists, or the equivalent NumPy array.
    - `xs` are the x coordinates of the points to plot. This parameter is optional and
      can either be a `None` or of the same shape as `ys`.
    - Any additional keyword arguments are passed to the `uniplot.options.Options` class.
    """
    series: MultiSeries = MultiSeries(xs=xs, ys=ys)
    options: Options = validate_and_transform_options(series=series, kwargs=kwargs)

    # Print header
    for line in _generate_header(options):
        print(line)

    # Main loop for interactive mode. Will only be executed once when not in interactive
    # mode.
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
        ) = _generate_body_raw_elements(series, options)

        # Delete plot before we re-draw
        if loop_iteration > 0:
            nr_lines_to_erase = options.height + 4
            if options.legend_labels is not None:
                nr_lines_to_erase += len(options.legend_labels)
            elements.erase_previous_lines(nr_lines_to_erase)

        for line in _generate_body(
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

            loop_iteration += 1


def plot_to_string(ys: Any, xs: Optional[Any] = None, **kwargs) -> List[str]:
    """
    Same as `plot`, but the return type is a list of strings. Ignores the `interactive` option.

    Can be used to integrate uniplot in other applications, or if the output is desired to be not stdout.
    """
    series: MultiSeries = MultiSeries(xs=xs, ys=ys)
    options: Options = validate_and_transform_options(series=series, kwargs=kwargs)

    header = _generate_header(options)
    (
        x_axis_labels,
        y_axis_labels,
        pixel_character_matrix,
    ) = _generate_body_raw_elements(series, options)

    body = _generate_body(x_axis_labels, y_axis_labels, pixel_character_matrix, options)
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

    - `xs` are the values of the points to plot. This parameter is mandatory and
      can either be a list or a list of lists, or the equivalent NumPy array.
    - Any additional keyword arguments are passed to the `uniplot.options.Options` class.
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


###########
# private #
###########


def _generate_header(options: Options) -> List[str]:
    """
    Generates the header of the plot, so everything above the first line of plottable area.
    """
    if options.title is None:
        return []

    return [elements.plot_title(options.title, width=options.width)]


def _generate_body(
    x_axis_labels: str,
    y_axis_labels: List[str],
    pixel_character_matrix: NDArray,
    options: Options,
) -> List[str]:
    """
    Generates the body of the plot.
    """
    lines: List[str] = []

    # Print plot (double resolution)
    lines.append(f"┌{'─'*options.width}┐")
    for i in range(options.height):
        row = pixel_character_matrix[i]
        lines.append(f"│{''.join(row)}│ {y_axis_labels[i]}")
    lines.append(f"└{'─'*options.width}┘")
    lines.append(x_axis_labels)

    # Print legend if labels were specified
    if options.legend_labels is not None:
        lines.append(elements.legend(options.legend_labels, width=options.width))

    return lines


def _generate_body_raw_elements(
    series: MultiSeries, options: Options
) -> Tuple[str, List[str], NDArray]:
    """
    Generates the x-axis labels, y-axis labels, and the pixel character matrix.
    """
    # Prepare y axis labels
    y_axis_label_set = extended_talbot_labels(
        x_min=options.y_min,
        x_max=options.y_max,
        available_space=options.height,
        unit=options.y_unit,
        log=options.y_as_log,
        vertical_direction=True,
    )
    y_axis_labels = [""] * options.height
    if y_axis_label_set is not None:
        y_axis_labels = y_axis_label_set.render()

    # Observe line_length_hard_cap
    if options.line_length_hard_cap is not None:
        options.reset_width()
        # Determine maximum length of y axis label
        max_y_label_length = max([len(l) for l in y_axis_labels])
        # Make sure the total plot does not exceed `line_length_hard_cap`
        if 2 + options.width + 1 + max_y_label_length > options.line_length_hard_cap:
            # Overflow, so we need to reduce width of plot area
            options.width = options.line_length_hard_cap - (2 + 1 + max_y_label_length)
            if options.width < 1:
                raise

    # Prepare x axis labels
    x_axis_label_set = extended_talbot_labels(
        x_min=options.x_min,
        x_max=options.x_max,
        available_space=options.width,
        unit=options.x_unit,
        log=options.x_as_log,
        vertical_direction=False,
    )
    x_axis_labels = ""
    if x_axis_label_set is not None:
        x_axis_labels = x_axis_label_set.render()[0]

    # Prepare graph surface
    pixel_character_matrix = layer_assembly.assemble_scatter_plot(
        xs=series.xs, ys=series.ys, options=options
    )

    return (x_axis_labels, y_axis_labels, pixel_character_matrix)
