from numpy.typing import NDArray
from typing import List

from uniplot.options import Options
import uniplot.layer_factory as layer_factory


def assemble_scatter_plot(
    xs: List[NDArray], ys: List[NDArray], options: Options
) -> NDArray:
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


def _merge_layers(character_layers: List[NDArray], options: Options) -> NDArray:
    merged_layer = layer_factory.blank_character_matrix(
        width=options.width, height=options.height
    )

    # Merge layers on top
    for character_layer in character_layers:
        # Just checking
        assert character_layer.shape == (options.height, options.width), (
            f"{character_layer.shape} != {(options.height, options.width)}"
        )
        to_replace_mask = character_layer != ""
        merged_layer[to_replace_mask] = character_layer[to_replace_mask]

    return merged_layer
