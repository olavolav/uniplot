import datetime

import numpy as np
import pytest

from uniplot import plot_gen, plot_to_string


@pytest.mark.parametrize(
    "fill",
    [
        True,
        False,
        np.bool_(True),
        float("nan"),
        float("inf"),
        1j,
        "zero",
        [[0]],
        [],
    ],
)
def test_invalid_fill(fill):
    with pytest.raises(ValueError, match="fill"):
        plot_to_string([1, 2], fill=fill)


@pytest.mark.parametrize("character_set", ["ascii", "block", "braille"])
def test_fill_is_independent_of_lines(character_set):
    output = plot_to_string(
        [3, 3],
        xs=[-1, 3],
        fill=0,
        x_min=0,
        x_max=2,
        y_min=0,
        y_max=2,
        width=3,
        height=2,
        border=None,
        x_labels=False,
        y_labels=False,
        x_gridlines=[],
        y_gridlines=[],
        character_set=character_set,
    )
    glyph = {"ascii": "+", "block": "█", "braille": "⣿"}[character_set]
    assert output == "\n".join([glyph * 3] * 2)


def test_fill_expands_bounds_and_can_be_cleared():
    p = plot_gen(ys=[10, 20], fill=np.int64(0))
    p.to_string()
    assert p.options.y_min < 0
    p.set_data(fill=None)
    p.to_string()
    assert p.options.y_min > 0


def test_single_point_does_not_expand_bounds():
    p = plot_gen(ys=[10], fill=-1000)
    p.to_string()
    assert p.options.y_min > 0


def test_per_series_fill_snapshot_and_length():
    fills = [0, None]
    p = plot_gen(ys=[[10, 20], [30, 40]], fill=fills)
    fills[0] = -1000
    p.to_string()
    assert -1 < p.options.y_min < 0
    p.set_data(ys=[10, 20])
    with pytest.raises(ValueError, match="fill"):
        p.to_string()


def test_log_baseline_transformed_once():
    p = plot_gen(ys=[10, 100], fill=1, y_as_log=True)
    p.to_string()
    assert p.options.fill == [0.0]
    p.set_data(ys=[10, 1000])
    p.to_string()
    assert p.options.fill == [0.0]
    for fill in [0, -1]:
        with pytest.raises(ValueError, match="fill"):
            plot_to_string([10, 100], fill=fill, y_as_log=True)


def test_datetime_and_numeric_baselines_match():
    ys = np.array(["2026-01-02", "2026-01-03"], dtype="datetime64[D]")
    date = datetime.date(2026, 1, 1)
    epoch = np.datetime64(date).astype("datetime64[s]").astype(float)
    assert plot_to_string(ys, fill=date) == plot_to_string(ys, fill=epoch)


def test_per_series_fill_uses_existing_character_and_overlap_order():
    output = plot_to_string(
        [[3, 3], [3, 3]],
        xs=[[-1, 3], [0.75, 1.25]],
        fill=[0, 0],
        x_min=0,
        x_max=2,
        y_min=0,
        y_max=2,
        width=3,
        height=2,
        character_set="ascii",
        force_ascii_characters=["a", "b"],
        color=False,
        border=None,
        x_labels=False,
        y_labels=False,
        x_gridlines=[],
        y_gridlines=[],
    )
    assert output == "aba\naba"


def test_log_x_fill_uses_transformed_segments():
    options = {
        "fill": 0,
        "width": 8,
        "height": 3,
        "border": None,
        "x_labels": False,
        "y_labels": False,
        "x_gridlines": [],
        "y_gridlines": [],
    }
    assert plot_to_string(
        [0, 2, 1], xs=[1, 10, 100], x_as_log=True, **options
    ) == plot_to_string([0, 2, 1], xs=[0, 1, 2], **options)


def test_resize_fill_and_restore():
    p = plot_gen(
        ys=[1, 3, 2],
        fill="bottom",
        width=20,
        height=2,
        border=None,
        x_labels=False,
        y_labels=False,
    )
    full = p.to_string()
    small = p.to_string(max_width=5)
    assert all(len(row) == 5 for row in small.splitlines())
    assert p.to_string() == full


def test_datetime_nat_breaks_fill():
    options = {
        "fill": "bottom",
        "width": 5,
        "height": 2,
        "border": None,
        "x_labels": False,
        "y_labels": False,
        "x_gridlines": [],
        "y_gridlines": [],
    }
    dates = np.array(["2026-01-02", "NaT", "2026-01-03"], dtype="datetime64[D]")
    # NaT must be a gap, never a finite timestamp near the int64 minimum.
    p = plot_gen(ys=dates, **options)
    p.to_string()
    assert np.isnan(p.series.ys[0][1])
    assert p.options.y_min > 0


def test_invalid_series_does_not_affect_another_filled_series():
    p = plot_gen(ys=[[np.nan, np.nan], [10, 20]], fill=[-1000, 0])
    p.to_string()
    assert -1 < p.options.y_min < 0


def test_infinite_data_is_a_gap_and_does_not_poison_bounds():
    p = plot_gen(ys=[10, np.inf, 20], fill=0)
    p.to_string()
    assert p.options.y_min > 0  # Neither isolated point has a filled area.


@pytest.mark.parametrize("invalid", [0, -1])
def test_nonpositive_log_samples_break_fill(invalid):
    options = {
        "fill": 1,
        "y_as_log": True,
        "y_min": 1,
        "y_max": 100,
        "x_min": 1,
        "x_max": 3,
        "x_gridlines": [],
        "y_gridlines": [],
    }
    assert plot_to_string([10, invalid, 100], **options) == plot_to_string(
        [10, np.nan, 100], **options
    )


def test_fill_scalar_broadcast():
    ys = [[1, 3], [2, 4]]
    assert plot_to_string(ys, fill=0) == plot_to_string(ys, fill=[0, 0])


def test_bottom_fill_tracks_pan_zoom_and_reset():
    ys = [1, 2, 1]
    p = plot_gen(ys=ys, fill="bottom", width=8, height=6, y_min=0, y_max=2)
    original = p.to_string()
    for operation in ("shift_view_down", "zoom_out", "reset_view"):
        getattr(p.options, operation)()
        bounds = {
            key: getattr(p.options, key) for key in ("x_min", "x_max", "y_min", "y_max")
        }
        assert p.to_string() == plot_to_string(
            ys, fill=bounds["y_min"], width=8, height=6, **bounds
        )
    assert p.to_string() == original


def test_pinned_y_bounds_survive_filled_data_updates():
    p = plot_gen(ys=[10, 20], fill=0, y_min=5, y_max=25)
    p.to_string()
    p.set_data(ys=[-100, 100])
    p.to_string()
    assert (p.options.y_min, p.options.y_max) == (5, 25)
    assert p.options.fill == [0.0]


def test_datetime_fill_revalidated_on_axis_type_change():
    p = plot_gen(
        ys=np.array(["2026-01-02", "2026-01-03"], dtype="datetime64[D]"),
        fill=np.datetime64("2026-01-01"),
    )
    p.to_string()
    p.set_data(ys=[1, 2])
    for _ in range(2):
        with pytest.raises(ValueError, match="fill"):
            p.to_string()
    p.set_data(fill=0)
    assert p.to_string() == plot_to_string([1, 2], fill=0)


def test_datetime_nat_baseline_rejected_on_datetime_axis():
    with pytest.raises(ValueError, match="fill"):
        plot_to_string(
            np.array(["2026-01-02", "2026-01-03"], dtype="datetime64[D]"),
            fill=np.datetime64("NaT"),
        )


def test_fill_without_valid_data_raises():
    with pytest.raises(ValueError):
        plot_to_string([np.nan, np.nan], fill=0)


def test_empty_fill_preserves_empty_plot_behavior():
    assert plot_to_string([], fill=0) == plot_to_string([])


@pytest.mark.parametrize("character_set", ["block", "braille"])
def test_foreground_point_keeps_existing_character_color_priority(character_set):
    options = {
        "width": 1,
        "height": 1,
        "x_min": 0,
        "x_max": 2,
        "y_min": 0,
        "y_max": 2,
        "border": None,
        "x_labels": False,
        "y_labels": False,
        "x_gridlines": [],
        "y_gridlines": [],
        "character_set": character_set,
    }
    actual = plot_to_string(
        [[3, 3], [1]],
        xs=[[-1, 3], [1]],
        fill=[0, None],
        color=["red", "blue"],
        **options,
    )
    expected = plot_to_string([1], xs=[1], color=["blue"], **options)
    assert actual == expected


def test_fill_covers_gridlines():
    options = {
        "fill": 0,
        "x_min": 0,
        "x_max": 2,
        "y_min": 0,
        "y_max": 2,
        "width": 5,
        "height": 3,
    }
    assert plot_to_string(
        [3, 3], xs=[-1, 3], x_gridlines=[1], y_gridlines=[1], **options
    ) == plot_to_string([3, 3], xs=[-1, 3], x_gridlines=[], y_gridlines=[], **options)
