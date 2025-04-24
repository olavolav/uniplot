from numpy.typing import NDArray
from typing import Tuple, List

from uniplot.multi_series import MultiSeries
from uniplot.options import Options
import uniplot.layer_assembly as layer_assembly
import uniplot.plot_elements as elements
from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels
from uniplot.axis_labels.datetime_labels import datetime_labels


def generate_header(options: Options) -> List[str]:
    """
    Generates the header of the plot, so everything above the first line of
    plottable area.
    """
    if options.title is None:
        return []

    return [
        elements.plot_title(
            options.title,
            width=options.width,
            line_length_hard_cap=options.line_length_hard_cap,
        )
    ]


def generate_body(
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
    lines.append(f"┌{'─' * options.width}┐")
    for y_label, row in zip(y_axis_labels, pixel_character_matrix):
        lines.append("│" + "".join(row) + "│ " + y_label)
    lines.append(f"└{'─' * options.width}┘")
    lines.append(x_axis_labels)

    # Print legend if labels were specified
    if options.legend_labels is not None:
        lines.append(
            elements.legend(
                options.legend_labels,
                width=options.width,
                line_length_hard_cap=options.line_length_hard_cap,
                color=options.color,
                force_ascii_characters=options.force_ascii_characters,
                character_set=options.character_set,
            )
        )

    return lines


def generate_body_raw_elements(
    series: MultiSeries, options: Options
) -> Tuple[str, List[str], NDArray]:
    """
    Generates the x-axis labels, y-axis labels, and the pixel character matrix.
    """
    # Prepare y axis labels
    label_fn = datetime_labels if series.y_is_time_series else extended_talbot_labels
    y_axis_label_set = label_fn(
        x_min=options.y_min,
        x_max=options.y_max,
        available_space=options.height,
        unit=options.y_unit,
        log=options.y_as_log,
        vertical_direction=True,
    )  # type: ignore
    y_axis_labels = [""] * options.height
    if y_axis_label_set is not None:
        y_axis_labels = y_axis_label_set.render()

    # Observe line_length_hard_cap
    if options.line_length_hard_cap is not None:
        options.reset_width()
        # Determine maximum length of y axis label
        max_y_label_length = max([len(ls) for ls in y_axis_labels])
        # Make sure the total plot does not exceed `line_length_hard_cap`
        if 2 + options.width + 1 + max_y_label_length > options.line_length_hard_cap:
            # Overflow, so we need to reduce width of plot area
            options.width = options.line_length_hard_cap - (2 + 1 + max_y_label_length)
            if options.width < 1:
                raise

    # Prepare x axis labels
    label_fn = datetime_labels if series.x_is_time_series else extended_talbot_labels
    x_axis_label_set = label_fn(
        x_min=options.x_min,
        x_max=options.x_max,
        available_space=options.width,
        unit=options.x_unit,
        log=options.x_as_log,
        vertical_direction=False,
    )  # type: ignore
    x_axis_labels = ""
    if x_axis_label_set is not None:
        x_axis_labels = x_axis_label_set.render()[0]

    # Prepare graph surface
    pixel_character_matrix = layer_assembly.assemble_scatter_plot(
        xs=series.xs, ys=series.ys, options=options
    )

    return (x_axis_labels, y_axis_labels, pixel_character_matrix)
