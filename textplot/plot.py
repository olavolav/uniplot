import numpy as np  # type: ignore
from typing import Optional

import textplot.pixel_matrix


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
        width=width,
        height=height,
    )

    # Print plot
    print(f"┌{'─'*width}┐ {y_max}")
    for row in range(height):
        pixel_row = [("*" if p > 0 else " ") for p in pixels[:, row]]
        print(f"│{''.join(pixel_row)}│")
    print(f"└{'─'*width}┘ {y_min}")
    print(f"{xs.min()} up to {xs.max()}")
