"""Tests for the Rich renderable integration on `plot_gen`."""

import builtins
import re

import pytest

from uniplot import plot_gen

# All tests here need rich; skip the whole module if it is not installed.
rich = pytest.importorskip("rich")
from rich.columns import Columns
from rich.console import Console
from rich.measure import Measurement
from rich.panel import Panel

ANSI_ESCAPE = re.compile(r"\033\[[\d;]+m")
YS = [1, 2, 4, 3, 5, 2]


def _render(renderable, width=80, no_color=False):
    console = Console(record=True, width=width, no_color=no_color, legacy_windows=False)
    console.print(renderable)
    return console.export_text()


def test_console_print_renders_plot():
    output = _render(plot_gen(ys=YS))
    # The plot box should be present.
    assert "┌" in output and "┘" in output


def test_no_raw_ansi_escapes_leak():
    # A colored plot printed through a no-color console must not contain raw
    # ANSI escape sequences; Rich should own all styling.
    output = _render(plot_gen(ys=[YS, [v + 1 for v in YS]], color=True), no_color=True)
    assert "\033[" not in output
    assert ANSI_ESCAPE.search(output) is None


def test_fits_inside_panel_without_overflow():
    width = 60
    output = _render(Panel(plot_gen(ys=YS)), width=width)
    for line in output.splitlines():
        assert len(line) <= width


def test_fits_inside_columns():
    output = _render(Columns([plot_gen(ys=YS), plot_gen(ys=YS)]), width=120)
    assert "┌" in output
    for line in output.splitlines():
        assert len(line) <= 120


def test_rich_measure_is_sane():
    console = Console(width=80)
    measurement = plot_gen(ys=YS).__rich_measure__(console, console.options)
    assert isinstance(measurement, Measurement)
    assert 0 < measurement.minimum <= measurement.maximum
    assert measurement.maximum <= console.options.max_width


def test_render_is_idempotent():
    plot = plot_gen(ys=YS)
    plot.to_string()  # force initial recompute (options are computed lazily)
    original_width = plot.options.width
    original_cap = plot.options.line_length_hard_cap

    first = plot.to_string()
    plot.to_string(max_width=40)
    second = plot.to_string()

    # Options are unchanged after rendering at different widths.
    assert plot.options.width == original_width
    assert plot.options.line_length_hard_cap == original_cap
    # Rendering without a width constraint is stable.
    assert first == second


def test_render_respects_max_width():
    plot = plot_gen(ys=YS)
    constrained = plot.to_string(max_width=40)
    for line in constrained.split("\n"):
        assert len(ANSI_ESCAPE.sub("", line)) <= 40


def test_single_render_path_equivalence():
    # to_string() and __rich_console__ must produce the same plot at the same
    # width, which guards against re-introducing a duplicate render path. (Rich
    # renders at the console width, so to_string() is given the same max_width.)
    width = 200
    via_to_string = plot_gen(ys=YS).to_string(max_width=width)

    console = Console(record=True, width=width, no_color=True, legacy_windows=False)
    console.print(plot_gen(ys=YS))
    via_rich = console.export_text()

    # Compare ignoring trailing whitespace per line (Rich pads to console width).
    def norm(s):
        return "\n".join(line.rstrip() for line in s.splitlines()).rstrip()

    assert norm(via_rich) == norm(via_to_string)


def test_live_smoke(monkeypatch):
    import io

    from rich.live import Live

    console = Console(file=io.StringIO(), width=80, force_terminal=True)
    plt = plot_gen(ys=[0.0], lines=True, y_min=-1.0, y_max=1.0)
    ys = []
    with Live(plt, console=console, refresh_per_second=4) as live:
        for i in range(20):
            ys.append((i % 5) - 2)
            plt.set_data(ys=ys[-10:])
        live.refresh()
    out = console.file.getvalue()
    assert "┌" in out


@pytest.mark.parametrize("fill", [None, "bottom"])
def test_set_data_is_thread_safe_under_render(fill):
    # Interleave set_data on one thread with rendering on another; the lock must
    # keep this from raising (e.g. torn options state). Both sides do a bounded
    # number of iterations and yield, so neither starves the other.
    import threading
    import time

    plt = plot_gen(ys=YS, fill=fill)
    errors = []

    def producer():
        for i in range(50):
            try:
                plt.set_data(ys=[v + (i % 3) for v in YS])
            except Exception as e:  # noqa: BLE001
                errors.append(e)
            time.sleep(0.001)

    t = threading.Thread(target=producer)
    t.start()
    try:
        for _ in range(50):
            try:
                plt.to_string(max_width=50)
            except Exception as e:  # noqa: BLE001
                errors.append(e)
            time.sleep(0.001)
    finally:
        t.join()
    assert not errors, errors[:3]


def test_helpful_error_when_rich_missing(monkeypatch):
    plot = plot_gen(ys=YS)
    console = Console(width=80)
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "rich.text" or name.startswith("rich.text"):
            raise ImportError("No module named 'rich.text'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match=r"pip install uniplot\[rich\]"):
        list(plot.__rich_console__(console, console.options))
