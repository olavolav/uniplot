"""
Smoke tests for the frontend.
"""

import datetime
import math
from random import random

import numpy as np
import pytest

from uniplot import (
    histogram,
    histogram_to_string,
    plot,
    plot_gen,
    plot_to_string,
    sparkline,
    sparkline_to_string,
)

################
# Testing plot #
################


def test_normal_plotting():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Sine wave")


def test_normal_plotting_with_x_series():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot(xs=x, ys=x, title="Diagonal")


def test_plotting_with_named_terminal_color():
    ys = [1, 3, -2, 5]
    plot(ys, color=["red"])


def test_plotting_with_single_named_terminal_color():
    """
    We want this to at least work, possibly with a warning, so that the
    options as so obvious that the user can guess them.
    """
    ys = [1, 3, -2, 5]
    plot(ys, color="red")


def test_plotting_with_rbg_color():
    ys = [1, 3, -2, 5]
    plot(ys, color=[(1, 2, 255)])


def test_plotting_with_color_theme():
    ys = [1, 3, -2, 5]
    plot(ys, color="mathematica")


def test_logarithmic_plotting():
    xs = range(1, 1000, 20)
    ys = [x**2 + 1e-6 for x in xs]
    plot(xs=xs, ys=ys, x_as_log=True, y_as_log=True)


def test_logarithmic_plot_gen_does_not_compound_log_across_updates():
    # The validator applies log scaling to the series in place. Re-rendering
    # must rebuild from the raw data so the log is applied exactly once, not
    # compounded (which previously turned the data into NaN and crashed).
    plt = plot_gen(
        ys=[0.0006, 0.0005, 0.0008, 0.003, 0.24], x_as_log=True, y_as_log=True
    )
    plt.to_string()
    first = list(plt.series.ys[0])
    plt.update()
    plt.update()
    assert list(plt.series.ys[0]) == first


def test_logarithmic_plotting_should_silently_ignore_invalid_values():
    ys = [-1.0, 0.0, 1.0, np.nan, 20.09, None, 12.2]
    plot(xs=ys, ys=ys, x_as_log=True, y_as_log=True)


def test_logarithmic_plotting_should_silently_ignore_invalid_values_even_in_2dim_case():
    ys = [-1.0, 0.0, 1.0, np.nan, 20.09, None, 12.2]
    plot([ys, ys], x_as_log=True, y_as_log=True)


def test_multi_series_plotting():
    ys = [
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) for i in range(1000)],
        # Make sure we also support plotting series of different length
        [math.sin(i / (10 + i / 50)) - math.sin(i / 100) - 1 for i in range(800)],
    ]
    plot(ys, title="Double sine wave", color=True)


def test_massively_multi_series_plotting():
    many_single_dot_series = [[math.sin(i / 20) + i / 300] for i in range(600)]
    plot(many_single_dot_series, title="Many colored dots", color=True)


def test_just_single_point_plotting():
    """
    Testing this because this has caused problems since for a single point min == max
    """
    x = [2.34]
    plot(x)


def test_with_rounded_corners():
    plot([1, 2, 3], rounded_corners=True)


def test_border_styles_with_axis_labels_hidden():
    options = {"width": 8, "height": 2, "x_labels": False, "y_labels": False}
    box = plot_to_string([1, 2, 3], border="box", **options).splitlines()
    rounded = plot_to_string([1, 2, 3], border="rounded", **options).splitlines()
    bare = plot_to_string(
        [1, 2, 3], border=None, line_length_hard_cap=8, **options
    ).splitlines()

    assert box[0] == "┌────────┐"
    assert rounded[0] == "╭────────╮"
    assert bare == [row[1:-1] for row in box[1:-1]]


def test_random_line_plotting():
    xs = [random() for _ in range(100)]
    ys = [random() for _ in range(100)]
    plot(xs=xs, ys=ys, lines=True)


def test_plotting_using_Braille_characters():
    xs = [random() for _ in range(100)]
    ys = [random() for _ in range(100)]
    plot(xs=xs, ys=ys, character_set="braille")


def test_plotting_with_colored_gridlines():
    plot(
        [1, 2, -3, 4],
        lines=True,
        y_gridlines_color=["red"],
        x_gridlines_color="tableau",
        x_gridlines=[-2, -1, 0, 0.5, 1.5, 2],
    )


def test_plotting_time_series_with_bounds_set_manually():
    dates = np.arange("2024-02-17T09:21", 4 * 60, 60, dtype="M8[m]")
    plot(xs=dates, ys=[1, 2, 3, 2], x_min=dates[0], x_max=dates[-1])


def test_plotting_time_series_with_auto_bounds():
    dates = np.arange("2024-02-17T09:21", 4 * 60, 60, dtype="M8[m]")
    plot(xs=dates, ys=[1, 2, 3, 2], x_min=dates[0], x_max=dates[-1])


def test_plotting_time_series_with_python_date_objects():
    dates = [datetime.date(year=2024, month=2, day=i) for i in range(1, 5)]
    plot(xs=dates, ys=[1, 2, 3, 2])


def test_plotting_time_series_with_python_datetime_objects():
    # Naive datetimes on purpose: that is what NumPy's `datetime64` supports.
    dates = [
        datetime.datetime(year=2024, month=2, day=i, hour=10, minute=5)  # noqa: DTZ001
        for i in range(1, 5)
    ]
    plot(xs=dates, ys=[1, 2, 3, 2])


def test_just_pass_objects_as_labels_works_as_well():
    class TestClass:
        def __init__(self, x) -> None:
            self.x: int = int(x)

        def __str__(self) -> str:
            return f"TestClass via str(x={self.x})"

        def __repr__(self) -> str:
            return f"TestClass via repr(x={self.x})"

    objects = [TestClass(1), TestClass(12), TestClass(123)]
    values = [[0, instance.x] for instance in objects]
    plot(values, title=objects[0], legend_labels=objects, lines=True)


def test_pass_some_empty_series():
    """
    This was issue #30.
    """
    plot([[1, 2, 3, 4, 3, 2, 3, 4], [3, 2, 2, 4, 1, 2, 1, 4], [1, 3], []], lines=True)


###########################
# Testing plot_to_string #
###########################


def test_normal_plotting_to_string():
    x = [math.sin(i / 20) + i / 300 for i in range(600)]
    plot_to_string(xs=x, ys=x, title="Sine wave")


def test_plotting_with_forced_ascii():
    ys = [1, 3, -2]
    strs = plot_to_string(
        xs=ys, ys=ys, title="Sine wave in ASCII", character_set="ascii"
    )
    assert "\n".join(strs).count("+") == len(ys)


def test_plotting_with_forced_ascii_and_custom_symbols():
    ys = [[1, 3, -2], [3, 4, 3, 4, 3, 5], [0]]
    symbols = ["A", "B", "C"]
    strs = plot_to_string(
        ys, character_set="ascii", color=False, force_ascii_characters=symbols
    )

    for i in range(len(symbols)):
        assert strs.count(symbols[i]) == len(ys[i])


def test_plotting_to_string_without_axis_labels():
    ys = [1, 2, 3]
    plot_to_string(ys, x_labels=False, y_labels=False)


####################
# Testing plot_gen #
####################


def test_plot_gen_init_and_update():
    plt = plot_gen(width=30)
    plt.update(ys=[1, 2, 3], title="Single update")


def test_plot_gen_update_without_changing_any_options():
    """
    This was issue #41.
    """
    plt = plot_gen(title="Test")
    plt.update(ys=[1, 2, 3])
    plt.update(ys=[1, 2, 3, 4])


# NOTE: `plot_gen` computes options lazily at render time, so these tests call
# `to_string()` to force a recompute before asserting on `plt.options`.


def test_plot_gen_explicit_bounds_are_pinned_across_updates():
    plt = plot_gen(ys=[1, 2, 3], y_min=-10, y_max=10)
    plt.set_data(ys=[1, 2, 3, 4])
    plt.to_string()
    assert (plt.options.y_min, plt.options.y_max) == (-10, 10)


def test_plot_gen_non_pinned_bounds_auto_range():
    plt = plot_gen(ys=[1, 2, 3])
    plt.set_data(ys=[1, 2, 3, 100])
    plt.to_string()
    assert plt.options.y_max > 50


def test_plot_gen_mixed_pin_only_one_bound():
    plt = plot_gen(ys=[1, 2, 3], y_max=999)
    plt.set_data(ys=[-50, 1, 2, 3])
    plt.to_string()
    # Pinned upper bound preserved, lower bound auto-ranges to cover -50.
    assert plt.options.y_max == 999
    assert plt.options.y_min < 0


def test_plot_gen_style_only_update_does_not_crash():
    # Previously raised KeyError: 'ys' (no data was ever supplied).
    assert isinstance(plot_gen().update(title="t"), str)
    assert isinstance(plot_gen(title="t").update(title="t2"), str)


def test_plot_gen_non_bound_options_persist_across_data_updates():
    plt = plot_gen(ys=[1, 2, 3], title="Persist", lines=True)
    plt.set_data(ys=[1, 2, 3, 4])
    plt.to_string()
    assert plt.options.title == "Persist"
    assert plt.options.lines == [True]


def test_plot_gen_pinned_bounds_dropped_on_data_type_change():
    import numpy as np

    # Float data with explicit (float) x bounds, which get pinned.
    plt = plot_gen(xs=[0, 1, 2, 3, 4], ys=[1.0, 2, 3, 2, 1], x_min=0, x_max=5)
    plt.to_string()
    assert plt.options.x_min == 0 and plt.options.x_max == 5

    # Switching to datetime data must drop the now-meaningless float pins so the
    # axis auto-ranges into timestamp space (~1.7e9), keeping points on screen.
    dates = np.array(
        ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        dtype="datetime64[s]",
    )
    plt.set_data(xs=dates, ys=[1.0, 2, 3, 2, 1])
    plt.to_string()
    assert plt.options.x_min > 1e9


def test_plot_gen_reset_view_clears_pins():
    plt = plot_gen(ys=[1, 2, 3], y_min=-10, y_max=10)
    plt.reset_view()
    assert plt._pinned_bounds == set()
    plt.set_data(ys=[1, 2, 3, 100])
    plt.to_string()
    # With pins cleared, the upper bound auto-ranges again.
    assert plt.options.y_max > 50


def test_plot_gen_update_returns_string():
    plt = plot_gen(ys=[1, 2, 3])
    out = plt.update(ys=[1, 2, 3, 4])
    assert isinstance(out, str)
    assert "┌" in out


def test_plot_gen_set_data_snapshots_against_later_mutation():
    """
    The `rich.live.Live` race: `set_data` is called with live lists that the
    producer keeps appending to, while the (expensive) recompute runs later on
    Rich's render thread. If we stored references, the producer's appends would
    desync the x- and y-series lengths and crash the render thread's length
    assertion. `set_data` must therefore snapshot the data at call time.
    """
    ys = [1.0, 2.0, 3.0]
    xs = [1, 2, 3]
    plt = plot_gen()
    plt.set_data(xs=xs, ys=ys)
    # Producer keeps appending after the call -- and drifts xs/ys apart.
    ys.append(4.0)
    ys.append(5.0)
    xs.append(4)
    # Rendering must neither crash nor reflect the post-call mutations.
    out = plt.to_string()
    assert isinstance(out, str)
    assert plt.series.shape() == [3]


def test_plot_gen_set_data_snapshots_inner_lists_of_multi_series():
    # An append to a live *inner* list must not desync the multi-series either.
    y0 = [1.0, 2.0, 3.0]
    y1 = [3.0, 2.0, 1.0]
    plt = plot_gen()
    plt.set_data(ys=[y0, y1])
    y0.append(99.0)
    plt.to_string()
    assert plt.series.shape() == [3, 3]


def test_plot_gen_set_data_snapshots_numpy_in_place_mutation():
    arr = np.array([1.0, 2.0, 3.0])
    plt = plot_gen()
    plt.set_data(ys=arr)
    arr[0] = 999.0  # in-place mutation after the call
    plt.to_string()
    assert plt.series.ys[0][0] == 1.0


def test_plot_gen_set_data_copy_false_skips_snapshot():
    # Escape hatch for producers that already hand over a fresh, private array
    # each tick and want zero snapshot overhead.
    arr = np.array([1.0, 2.0, 3.0])
    plt = plot_gen()
    plt.set_data(ys=arr, copy=False)
    assert plt._raw_ys is arr


def test_plot_gen_set_data_snapshots_mutable_options():
    """
    Mutable *option* values (here a per-series `lines` list) must be snapshotted
    too, not just `xs`/`ys`. Otherwise a producer mutating the list it passed can
    desync it from the series count and raise `ValueError("Invalid 'lines'
    option.")` on the background render thread -- the same race as for data.
    """
    lines = [True, True]
    plt = plot_gen()
    plt.set_data(ys=[[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]], lines=lines)
    lines.append(True)  # now len 3 != 2 series -> would crash the renderer
    out = plt.to_string()
    assert isinstance(out, str)
    assert plt.options.lines == [True, True]


def test_plot_gen_set_data_copy_false_skips_option_snapshot():
    lines = [True, True]
    plt = plot_gen()
    plt.set_data(ys=[[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]], lines=lines, copy=False)
    assert plt._option_kwargs["lines"] is lines


#####################
# Testing histogram #
#####################


def test_plotting_a_histogram():
    xs = [1, 2, 3, 2, 3, 2, 1]
    histogram(xs)


def test_plotting_a_histogram_of_datetimes_shows_date_labels():
    # A histogram of a datetime64 series must render its x-axis as dates, not
    # as raw epoch numbers (see issue: timestamp display for histogram X axis).
    base = np.datetime64("2002-10-27T04:30", "ns")
    dates = base + (np.arange(100) * np.timedelta64(1, "h")).astype("m8[ns]")
    output = histogram_to_string(dates, bins=5)
    assert "2002-1" in output
    # The raw epoch seconds (~1.03e9) must not leak into the axis labels.
    assert "1,035" not in output and "1035" not in output


###############################
# Testing histogram_to_string #
###############################


def test_plotting_a_histogram_to_string():
    xs = [1, 2, 3, 2, 3, 2, 1]
    histogram_to_string(xs)


#####################
# Testing sparkline #
#####################


def test_sparkline_prints_string_result(capsys):
    options = {"color": ["green"], "y_min": 0, "y_max": 10}
    sparkline([1, 3, 2, 5, 4], width=10, **options)
    output = capsys.readouterr().out

    assert output == sparkline_to_string([1, 3, 2, 5, 4], width=10, **options) + "\n"


@pytest.mark.parametrize("ys,width", [([1], 1), ([2, 2, 2], 5), ([1, 3, 2, 5, 4], 10)])
def test_sparkline_string_dimensions(ys, width):
    output = sparkline_to_string(ys, width=width)

    assert output.splitlines() == [output]
    assert len(output) == width


def test_sparkline_fills_to_bottom_without_plot_decorations():
    assert sparkline_to_string([0, 1], width=5) == "⣀⣤⣶⣶⣿"


@pytest.mark.parametrize(
    "bounds", [{"y_min": 0}, {"y_max": 10}, {"y_min": 0, "y_max": 10}]
)
def test_sparkline_uses_explicit_bounds(bounds):
    ys = [3, 5, 4]
    expected = plot_to_string(
        ys,
        width=8,
        height=1,
        border=None,
        fill="bottom",
        lines=True,
        x_labels=False,
        y_labels=False,
        x_gridlines=[],
        y_gridlines=[],
        character_set="braille",
        **bounds,
    )
    output = sparkline_to_string(ys, width=8, **bounds)
    assert output == expected


def test_sparkline_color():
    plain = sparkline_to_string([1, 3, 2], color=False)
    colored = sparkline_to_string([1, 3, 2], color=["green"])
    assert "\033[32m" in colored
    assert colored.replace("\033[32m", "").replace("\033[0m", "") == plain
