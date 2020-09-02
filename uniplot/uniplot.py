import numpy as np  # type: ignore
from typing import List, Optional

from uniplot.options import Options
import uniplot.layer_assembly as layer_assembly
import uniplot.plot_elements as elements
from uniplot.getch import getch


def plot(ys: np.array, xs: Optional[np.array] = None, **kwargs) -> None:
    """
    2D scatter dot plot on the terminal.

    Parameters:

    - `ys` are the y coordinates of the points to plot. This parameter is mandatory and
      can either be a list or a list of lists, or the equivalent NumPy array.
    - `xs` are the x coordinates of the points to plot. This parameter is optional and
      can either be a `None` or of the same shape as `ys`.
    - Any additional keyword arguments are passed to the `uniplot.options.Options` class.
    """

    # Initialize mandatory parameter `ys` as NumPy array
    ys = np.array(ys)
    assert len(ys.shape) <= 2

    # Initialize optional parameter `xs` as NumPy array
    if xs is None:
        if len(ys.shape) == 1:
            xs = np.arange(1, len(ys) + 1, step=1, dtype=int)
        else:
            xs = np.array([np.arange(1, len(ysi) + 1, step=1, dtype=int) for ysi in ys])
    else:
        xs = np.array(xs)
    # Make sure that the end result looks good
    assert ys.shape == xs.shape

    # Set bounds to show all points by default
    kwargs["x_min"] = kwargs.get("x_min") or xs.min()
    kwargs["x_max"] = kwargs.get("x_max") or (xs.max() + 1e-4 * (xs.max() - xs.min()))
    if float(kwargs["x_min"]) == float(kwargs["x_max"]):
        kwargs["x_min"] = kwargs["x_min"] - 1
        kwargs["x_max"] = kwargs["x_max"] + 1
    kwargs["y_min"] = kwargs.get("y_min") or ys.min()
    kwargs["y_max"] = kwargs.get("y_max") or (ys.max() + 1e-4 * (ys.max() - ys.min()))
    if float(kwargs["y_min"]) == float(kwargs["y_max"]):
        kwargs["y_min"] = kwargs["y_min"] - 1
        kwargs["y_max"] = kwargs["y_max"] + 1
    print(f"DEBUG: kwargs = {kwargs}")
    options = Options(**kwargs)

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

        # Prepare plot elements
        y_axis_labels = elements.yaxis_ticks(
            y_min=options.y_min, y_max=options.y_max, height=options.height
        )
        x_axis_labels = elements.xaxis_ticks(
            x_min=options.x_min, x_max=options.x_max, width=options.width
        )

        # Prefare graph surface
        pixel_character_matrix = layer_assembly.assemble_scatter_plot(
            xs=xs, ys=ys, options=options
        )

        # Delete plot before we re-draw
        if loop_iteration > 0:
            elements.erase_previous_lines(options.height + 4)

        # Print plot (double resolution)
        print(f"┌{'─'*options.width}┐")
        for i in range(options.height):
            row = pixel_character_matrix[i]
            print(f"│{''.join(row)}│ {y_axis_labels[i]}")
        print(f"└{'─'*options.width}┘")
        print(x_axis_labels)

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
                # Reset view
                options.x_min = xs.min()
                options.x_max = xs.max()
                options.y_min = ys.min()
                options.y_max = ys.max()
            elif key_pressed in ["q", "\x1b"]:
                # q and Escape will end interactive mode
                continue_looping = False

            loop_iteration += 1
