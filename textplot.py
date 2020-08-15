import numpy as np  # type: ignore
from typing import Optional


def plot(
    ys: np.array,
    xs: Optional[np.array] = None,
    width: int = 60,
    height: int = 16,
    title: Optional[str] = None,
    color: Optional[str] = None,
) -> None:
    """2D scatter dot plot on the terminal."""
    if xs is None:
        xs = np.arange(1, len(ys) + 1, step=1, dtype=int)
    max_y = ys.max()
    min_y = ys.min()

    # Print title
    if title is not None:
        if len(title) >= width:
            print(title)
        else:
            offset = int((width + 2 - len(title)) / 2)
            print((" " * offset) + title)

    # Put occurrences into pixel matrix
    pixels = np.zeros((width, height), dtype=int)
    i = 0
    for y in ys:
        # TODO Optimize as vector operations
        x_pixel = int(1.0 * i / (len(ys) - 1) * width - 0.0001)
        y_pixel = int(height - (y - min_y) / (max_y - min_y) * height - 0.0001)
        pixels[x_pixel, y_pixel] = 1
        i = i + 1

    # Print plot
    print(f"┌{'─'*width}┐ {max_y}")
    for row in range(height):
        pixel_row = [("*" if p > 0 else " ") for p in pixels[:, row]]
        print(f"│{''.join(pixel_row)}│")
    print(f"└{'─'*width}┘ {min_y}")
    print(f"{xs.min()} up to {xs.max()}")
