import numpy as np  # type: ignore
from typing import Optional

import textplot.pixel_matrix
from textplot.plot_elements import character_for_2by2_pixels


def plot(
    ys: np.array,
    xs: Optional[np.array] = None,
    width: int = 60,
    height: int = 16,
    title: Optional[str] = None,
    color: Optional[str] = None,
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

    # Print plot (single resolution)
    # print(f"┌{'─'*width}┐ {y_max}")
    # for row in range(height):
    #     pixel_row = [("*" if p > 0 else " ") for p in pixels[:, row]]
    #     print(f"│{''.join(pixel_row)}│")
    # print(f"└{'─'*width}┘ {y_min}")

    # Print plot (double resolution)
    print(f"┌{'─'*width}┐ {y_max}")
    for row in range(height):
        pixel_row = [
            character_for_2by2_pixels(pixels[2 * row : 2 * row + 2, 2 * i : 2 * i + 2])
            for i in range(width)
        ]
        print(f"│{''.join(pixel_row)}│")
    print(f"└{'─'*width}┘ {y_min}")
    print(f"{xs.min()} up to {xs.max()}")
