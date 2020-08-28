import numpy as np  # type: ignore
from typing import List

from uniplot.options import Options
import uniplot.layer_factory as layer_factory


def assemble_scatter_plot(xs: np.array, ys: np.array, options: Options) -> np.array:
    """
    Assemble the graph surface for a scatter plot.
    """

    # Gridlines
    horizontal_gridline_layers = [
        layer_factory.render_horizontal_gridline(y=y, options=options)
        for y in options.y_gridlines
    ]
    vertical_gridline_layers = [
        layer_factory.render_vertical_gridline(x=x, options=options)
        for x in options.x_gridlines
    ]

    # Pixels
    pixel_layer = layer_factory.render_points(xs=xs, ys=ys, options=options)

    # Assemble graph surface
    all_layers = horizontal_gridline_layers + vertical_gridline_layers + [pixel_layer]
    return _merge_layers(all_layers, options=options)


###########
# private #
###########


def _merge_layers(character_layers: List[np.array], options: Options) -> np.array:
    # Initialize with blank layer consisting of spaces only
    merged_layer = layer_factory.blank_pixel_character_matrix(
        width=options.width, height=options.height
    )

    # Merge layers on top
    for character_layer in character_layers:
        # Just checking
        assert character_layer.shape == (options.height, options.width)

        for row_index in range(options.height):
            for column_index in range(options.width):
                if character_layer[row_index, column_index] != "":
                    merged_layer[row_index, column_index] = character_layer[
                        row_index, column_index
                    ]

    return merged_layer
