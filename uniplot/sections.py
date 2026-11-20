from functools import partial

from numpy.typing import NDArray

import uniplot.plot_elements as elements
from uniplot import layer_assembly
from uniplot.axis_labels.datetime_labels import datetime_labels
from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels
from uniplot.multi_series import MultiSeries
from uniplot.options import Options


def generate_header(options: Options) -> list[str]:
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
            border_width=0 if options.border is None else 2,
        )
    ]


def generate_body(
    x_axis_labels: str,
    y_axis_labels: list[str],
    pixel_character_matrix: NDArray,
    options: Options,
) -> list[str]:
    """
    Generates the body of the plot.
    """

    lines: list[str] = []
    corners = {"box": "┌┐└┘", "rounded": "╭╮╰╯"}.get(options.border or "")
    side = "│" if corners else ""
    edge = "─" * options.width
    if corners:
        lines.append(f"{corners[0]}{edge}{corners[1]}")
    for y_label, row in zip(y_axis_labels, pixel_character_matrix):
        suffix = f" {y_label}" if y_label else ""
        lines.append(f"{side}{''.join(row)}{side}{suffix}")
    if corners:
        lines.append(f"{corners[2]}{edge}{corners[3]}")

    if len(x_axis_labels) > 0:
        lines.append(x_axis_labels)

    # Add legend labels, if labels were specified
    if options.legend_labels is not None:
        lines.append(
            elements.legend(
                options.legend_labels,
                width=options.width,
                line_length_hard_cap=options.line_length_hard_cap,
                color=options.color,
                force_ascii_characters=options.force_ascii_characters,
                character_set=options.character_set,
                legend_placement=options.legend_placement,
                border_width=0 if options.border is None else 2,
            )
        )

    return lines


def generate_body_raw_elements(
    series: MultiSeries, options: Options
) -> tuple[str, list[str], NDArray]:
    """
    Generates the x-axis labels, y-axis labels, and the pixel character matrix.
    """
    # Prepare y axis labels
    y_axis_labels = [""] * options.height
    if options.y_labels:
        label_fn = (
            partial(datetime_labels, timezone=series.y_timezone)
            if series.y_is_time_series
            else extended_talbot_labels
        )
        y_axis_label_set = label_fn(
            x_min=options.y_min,
            x_max=options.y_max,
            available_space=options.height,
            unit=options.y_unit,
            unit_scaling=options.y_unit_scaling,
            log=options.y_as_log,
            vertical_direction=True,
        )  # type: ignore
        if y_axis_label_set is not None:
            y_axis_labels = y_axis_label_set.render()

    # Observe line_length_hard_cap
    if options.line_length_hard_cap is not None:
        options.reset_width()
        max_y_label_length = max(len(label) for label in y_axis_labels)
        label_width = 1 + max_y_label_length if max_y_label_length else 0
        border_width = 0 if options.border is None else 2
        options.width = min(
            options.width, options.line_length_hard_cap - border_width - label_width
        )
        if options.width < 1:
            raise ValueError("`width` must be greater than zero.")

    # Prepare x axis labels
    x_axis_labels = ""
    if options.x_labels:
        label_fn = (
            partial(datetime_labels, timezone=series.x_timezone)
            if series.x_is_time_series
            else extended_talbot_labels
        )
        x_axis_label_set = label_fn(
            x_min=options.x_min,
            x_max=options.x_max,
            available_space=options.width,
            unit=options.x_unit,
            unit_scaling=options.x_unit_scaling,
            log=options.x_as_log,
            vertical_direction=False,
            left_margin=0 if options.border is None else 1,
        )  # type: ignore
        if x_axis_label_set is not None:
            x_axis_labels = x_axis_label_set.render()[0]

    # Prepare graph surface
    pixel_character_matrix = layer_assembly.assemble_scatter_plot(
        xs=series.xs, ys=series.ys, options=options
    )

    return (x_axis_labels, y_axis_labels, pixel_character_matrix)
