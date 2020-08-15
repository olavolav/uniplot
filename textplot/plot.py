import numpy as np  # type: ignore
from typing import Optional

import textplot.pixel_matrix
import textplot.plot_elements as elements
from textplot.getch import getch


def plot(
    ys: np.array,
    xs: Optional[np.array] = None,
    width: int = 60,
    height: int = 17,
    title: Optional[str] = None,
    color: Optional[str] = None,
    interactive: bool = False,
) -> None:
    """2D scatter dot plot on the terminal."""
    ys = np.array(ys)
    if xs is None:
        xs = np.arange(1, len(ys) + 1, step=1, dtype=int)

    # Define view
    # TODO Make this a dataclass and expand the initial view by a few percent
    x_min = xs.min()
    x_max = xs.max()
    y_min = ys.min()
    y_max = ys.max()

    # Print title
    if title is not None:
        if len(title) >= width:
            print(title)
        else:
            offset = int((width + 2 - len(title)) / 2)
            print((" " * offset) + title)

    # Main loop for interactive mode. Will only be executed once when not in interactive # mode.
    continue_looping: bool = True
    loop_iteration: int = 0
    while continue_looping:
        # Make sure we stop after first iteration when not in interactive mode
        if not interactive:
            continue_looping = False

        pixels = textplot.pixel_matrix.render(
            xs,
            ys,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            width=2 * width,
            height=2 * height,
        )

        # Prepare plot elements
        y_axis_labels = elements.yaxis_ticks(y_min=y_min, y_max=y_max, height=height)
        x_axis_labels = elements.xaxis_ticks(x_min=x_min, x_max=x_max, width=width)

        # Delete plot before we re-draw
        if loop_iteration > 0:
            elements.erase_previous_lines(height + 4)

        # Print plot (single resolution)
        # print(f"┌{'─'*width}┐ {y_max}")
        # for row in range(height):
        #     pixel_row = [("*" if p > 0 else " ") for p in pixels[:, row]]
        #     print(f"│{''.join(pixel_row)}│")
        # print(f"└{'─'*width}┘ {y_min}")

        # Print plot (double resolution)
        print(f"┌{'─'*width}┐")
        for row in range(height):
            pixel_row = [
                elements.character_for_2by2_pixels(
                    pixels[2 * row : 2 * row + 2, 2 * i : 2 * i + 2]
                )
                for i in range(width)
            ]
            print(f"│{''.join(pixel_row)}│ {y_axis_labels[row]}")
        print(f"└{'─'*width}┘")
        print(x_axis_labels)

        if interactive:
            print(
                "Interactive mode: Move viewport using h/j/k/l, zoom via u/n, or r to reset the view. Escape or q to quit"
            )
            key_pressed = getch()
            if key_pressed == "h":
                # Left
                step = 0.1 * (x_max - x_min)
                x_min = x_min - step
                x_max = x_max - step
            elif key_pressed == "l":
                # Right
                step = 0.1 * (x_max - x_min)
                x_min = x_min + step
                x_max = x_max + step
            elif key_pressed == "j":
                # Up
                step = 0.1 * (y_max - y_min)
                y_min = y_min - step
                y_max = y_max - step
            elif key_pressed == "k":
                # Down
                step = 0.1 * (y_max - y_min)
                y_min = y_min + step
                y_max = y_max + step
            elif key_pressed == "u":
                # Zoom in
                step = 0.1 * (x_max - x_min)
                x_min = x_min + step
                x_max = x_max - step
                step = 0.1 * (y_max - y_min)
                y_min = y_min + step
                y_max = y_max - step
            elif key_pressed == "n":
                # Zoom out
                step = 0.1 * (x_max - x_min)
                x_min = x_min - step
                x_max = x_max + step
                step = 0.1 * (y_max - y_min)
                y_min = y_min - step
                y_max = y_max + step
            elif key_pressed == "r":
                # Reset view
                x_min = xs.min()
                x_max = xs.max()
                y_min = ys.min()
                y_max = ys.max()
            elif key_pressed in ["q", "Q", "\x1b"]:
                # q, Enter and Escape will end interactive mode
                continue_looping = False

            loop_iteration += 1
