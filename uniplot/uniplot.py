import numpy as np  # type: ignore
from typing import List, Optional, Any

from uniplot.multi_series import MultiSeries
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
    series = MultiSeries(xs=xs, ys=ys)
    options = validate_and_transform_options(series=series, kwargs=kwargs)

    # Print title
    if options.title is not None:
        print(elements.plot_title(options.title, width=options.width))

    # Main loop for interactive mode. Will only be executed once when not in interactive # mode.
    continue_looping: bool = True
    loop_iteration: int = 0
    while continue_looping:
        # Make sure we stop after first iteration when not in interactive mode
        if not options.interactive:
            continue_looping = False

        # Prepare y axis labels
        y_axis_labels = ["-error generating labels, sorry-"] * options.height
        y_axis_label_set = extended_talbot_labels(
            x_min=options.y_min,
            x_max=options.y_max,
            available_space=options.height,
            vertical_direction=True,
        )
        if y_axis_label_set is not None:
            y_axis_labels = y_axis_label_set.render()

        # Prepare x axis labels
        x_axis_label_set = extended_talbot_labels(
            x_min=options.x_min,
            x_max=options.x_max,
            available_space=options.width,
            vertical_direction=False,
        )
        x_axis_labels = "-error generating labels, sorry-"
        if x_axis_label_set is not None:
            x_axis_labels = x_axis_label_set.render()[0]

        # Prefare graph surface
        pixel_character_matrix = layer_assembly.assemble_scatter_plot(
            xs=series.xs, ys=series.ys, options=options
        )

        # Delete plot before we re-draw
        if loop_iteration > 0:
            nr_lines_to_erase = options.height + 4
            if options.legend_labels is not None:
                nr_lines_to_erase += len(options.legend_labels)
            elements.erase_previous_lines(nr_lines_to_erase)

        # Print plot (double resolution)
        print(f"┌{'─'*options.width}┐")
        for i in range(options.height):
            row = pixel_character_matrix[i]
            print(f"│{''.join(row)}│ {y_axis_labels[i]}")
        print(f"└{'─'*options.width}┘")
        print(x_axis_labels)

        # Print legend if labels were specified
        # TODO Fix erase during interactive mode
        if options.legend_labels is not None:
            print(elements.legend(options.legend_labels, width=options.width))

        if options.interactive:
            print("Move h/j/k/l, zoom u/n, or r to reset. ESC/q to quit")
            key_pressed = getch().lower()

            # TODO Move all of the below to the `Options` class
            if key_pressed == "h":
                # Left
                step = 0.1 * (options.x_max - options.x_min)
                options.x_min = options.x_min - step
                options.x_max = options.x_max - step
            elif key_pressed == "l":
                # Right
                step = 0.1 * (options.x_max - options.x_min)
                options.x_min = options.x_min + step
                options.x_max = options.x_max + step
            elif key_pressed == "j":
                # Up
                step = 0.1 * (options.y_max - options.y_min)
                options.y_min = options.y_min - step
                options.y_max = options.y_max - step
            elif key_pressed == "k":
                # Down
                step = 0.1 * (options.y_max - options.y_min)
                options.y_min = options.y_min + step
                options.y_max = options.y_max + step
            elif key_pressed == "u":
                # Zoom in
                step = 0.1 * (options.x_max - options.x_min)
                options.x_min = options.x_min + step
                options.x_max = options.x_max - step
                step = 0.1 * (options.y_max - options.y_min)
                options.y_min = options.y_min + step
                options.y_max = options.y_max - step
            elif key_pressed == "n":
                # Zoom out
                step = 0.1 * (options.x_max - options.x_min)
                options.x_min = options.x_min - step
                options.x_max = options.x_max + step
                step = 0.1 * (options.y_max - options.y_min)
                options.y_min = options.y_min - step
                options.y_max = options.y_max + step
            elif key_pressed == "r":
                options.reset_view()
            elif key_pressed in ["q", "\x1b"]:
                # q and Escape will end interactive mode
                continue_looping = False

            loop_iteration += 1


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
        hist, bin_edges = np.histogram(s, bins=bins, range=(bins_min, bins_max))
        xs_here = np.zeros(1 + 2 * bins + 1)
        ys_here = np.zeros(1 + 2 * bins + 1)
        xs_here[0] = bin_edges[0]
        xs_here[1::2] = bin_edges
        xs_here[2::2] = bin_edges[1:]
        # ys_here[0] = 0
        ys_here[1:-1:2] = hist
        ys_here[2:-1:2] = hist
        # ys_here[-1] = 0

        xs_histo_series.append(xs_here)
        ys_histo_series.append(ys_here)

    plot(xs=xs_histo_series, ys=ys_histo_series, **kwargs)
