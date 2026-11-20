import threading
from typing import TYPE_CHECKING, Any, Final

import numpy as np
from readchar import key, readkey

import uniplot.plot_elements as elements
from uniplot import colors, sections
from uniplot.multi_series import MultiSeries
from uniplot.options import Options
from uniplot.param_initializer import validate_and_transform_options

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult
    from rich.measure import Measurement

# The four view-window bounds, tracked separately from other options because
# they can be "pinned" (preserved across updates) by an explicit option or by
# interactive pan/zoom, while everything else auto-ranges from the data.
_BOUND_KEYS: Final[tuple[str, ...]] = ("x_min", "x_max", "y_min", "y_max")


def plot(ys: Any, xs: Any | None = None, **kwargs) -> None:
    """
    2D plot on the terminal.

    Parameters:

    - `ys` are the y coordinates of the points to plot. This parameter is
      mandatory and can either be a list or a list of lists, or the equivalent
      NumPy array.
    - `xs` are the x coordinates of the points to plot. This parameter is
      optional and can either be a `None` or of the same shape as `ys`.
    - Any additional keyword arguments are passed to the
      `uniplot.options.Options` class.
    """
    plt = plot_gen()

    # Main loop for interactive mode. Will only be executed once when not in
    # interactive mode. The data is supplied on the first iteration only, so it
    # is processed exactly once; later iterations just re-render the view.
    first_iteration: bool = True
    while first_iteration or plt.options.interactive:
        if first_iteration:
            plt.update(xs=xs, ys=ys, **kwargs)
        else:
            plt.update()

        if plt.options.interactive:
            plt.print_subscript("Move h/j/k/l, zoom u/n, or r to reset. q to quit.")
            key_pressed = readkey()

            # Here we support 3 ways to move: Vim-style, arrow keys and FPS-style.
            # Panning/zooming pins the affected bounds, so they are preserved on
            # the next `update()` instead of being auto-ranged away.
            if key_pressed in ["h", key.LEFT, "a"]:
                plt.options.shift_view_left()
                plt._pinned_bounds |= {"x_min", "x_max"}
            elif key_pressed in ["l", key.RIGHT, "d"]:
                plt.options.shift_view_right()
                plt._pinned_bounds |= {"x_min", "x_max"}
            elif key_pressed in ["j", key.DOWN, "s"]:
                plt.options.shift_view_down()
                plt._pinned_bounds |= {"y_min", "y_max"}
            elif key_pressed in ["k", key.UP, "w"]:
                plt.options.shift_view_up()
                plt._pinned_bounds |= {"y_min", "y_max"}
            elif key_pressed in ["u", "]"]:
                plt.options.zoom_in()
                plt._pinned_bounds |= set(_BOUND_KEYS)
            elif key_pressed in ["n", "["]:
                plt.options.zoom_out()
                plt._pinned_bounds |= set(_BOUND_KEYS)
            elif key_pressed == "r":
                plt.reset_view()
            elif key_pressed in ["q", "Q", key.ESC]:
                break

        first_iteration = False


class plot_gen:
    """
    Stateful plot object, used for streaming, repeated updates and as a Rich
    renderable.

    Every `update()` re-draws from scratch (relying on caching). The only state
    kept is the data, the options, which view bounds are "pinned", the
    accumulated non-data options, and the number of lines last printed (so the
    previous frame can be erased).
    """

    def __init__(self, return_string=False, **kwargs) -> None:
        if return_string:
            raise ValueError(
                "The `return_string` argument was removed. "
                "Use `plot_to_string(...)` or `plot_gen.to_string()` instead."
            )

        self.series: MultiSeries = MultiSeries([])
        self.options: Options = Options()
        # The raw, untransformed data as last supplied by the user. The series
        # is rebuilt from this on every render so that in-place transforms in
        # the validator (e.g. log scaling) are applied exactly once instead of
        # being compounded across updates.
        self._raw_xs: Any = None
        self._raw_ys: Any = None
        # Bound keys (subset of `_BOUND_KEYS`) that should be preserved across
        # updates rather than auto-ranged.
        self._pinned_bounds: set = set()
        # Explicit bound values supplied but not yet applied (carried across
        # coalesced updates until the next recompute).
        self._pending_bound_values: dict = {}
        # Non-data, non-bound options that persist across updates (e.g. `title`,
        # `color`, `lines`, `width`), so a data-only `update(ys=...)` keeps them.
        self._option_kwargs: dict = {}
        # Whether new data/options have been ingested since the last recompute.
        self._dirty: bool = False
        self.last_nr_of_lines: int = 0
        # Guards ingestion against rendering, so the object is safe to use with
        # `rich.live.Live` (which renders on a background thread while the
        # producer calls `set_data`). Ingestion is intentionally cheap, so a
        # high-rate producer cannot starve the renderer.
        self._lock = threading.Lock()
        if kwargs:
            self._ingest(kwargs)

    def update(self, **kwargs) -> str:
        """
        Apply any new data/options, then re-draw in place on the terminal
        (erasing the previous frame). Returns the rendered string as well, so it
        can also be captured (e.g. for logging).
        """
        self._ingest(kwargs)
        output = self._render()
        elements.erase_previous_lines(self.last_nr_of_lines)
        self.last_nr_of_lines = elements.count_lines(output)
        print(output)
        return output

    def set_data(self, copy: bool = True, **kwargs) -> None:
        """
        Record new data/options without rendering or printing. Intended for use
        with `rich.live.Live`, where Rich owns the screen and re-renders the
        object on its own schedule; the (potentially expensive) recompute then
        happens once per rendered frame rather than once per call.

        By default the supplied data *and* any mutable option values are
        snapshotted at call time, so it is safe to hand over live, still-growing
        lists: the producer can keep appending without desyncing them or crashing
        the render thread. The snapshot is cheap (see `_defensive_copy`). Pass
        `copy=False` to skip it when you already hand over fresh, private objects
        each call and want zero overhead.

        Accumulation across calls:

        - Options (e.g. `title`, `lines`, `color`) *accumulate*: each is kept
          until you pass that key again, so a later call need only send what
          changed. Passing a key again overwrites it (last value wins).
        - Explicit bounds (`x_min`/`x_max`/`y_min`/`y_max`) are additionally
          *pinned* and preserved across later data updates, until `reset_view()`
          or an axis data-type change (e.g. numeric <-> datetime).
        - Data is *replaced*, not accumulated: passing `ys` swaps the whole
          series. `ys` without `xs` resets the x-axis to the serial index `1..N`
          (x and y are one coupled unit), so to keep a custom x-axis pass `xs`
          together with `ys` every time. A lone `xs` (no `ys`) is ignored.

        Note that `self.options` reflects the new data only after the next
        render (e.g. via `to_string()` or a `Live` refresh).
        """
        self._ingest(kwargs, copy=copy)

    def to_string(self, max_width: int | None = None) -> str:
        """
        Return the current plot as a string, without printing.
        """
        return self._render(max_width)

    def reset_view(self) -> None:
        """
        Reset the view window to its initial bounds and clear all pins, so
        subsequent renders auto-range again.
        """
        with self._lock:
            self.options.reset_view()
            self._pinned_bounds.clear()
            self._pending_bound_values.clear()
            self._dirty = True

    def print_subscript(self, text: str) -> None:
        self.last_nr_of_lines += elements.count_lines(text)
        print(text)

    def _ingest(self, kwargs: dict, copy: bool = True) -> None:
        """
        Record new data/options cheaply and mark the plot dirty. The expensive
        recompute is deferred to the next render (`_recompute`), so a high-rate
        producer does not starve the renderer and the heavy work runs once per
        rendered frame rather than once per update.

        Unless `copy=False`, the data is snapshotted here (synchronously, on the
        caller's thread) so later mutation by the producer cannot affect a
        deferred render -- the crux of thread-safety with `rich.live.Live`.
        """
        with self._lock:
            kwargs = dict(kwargs)
            has_ys = "ys" in kwargs
            xs = kwargs.pop("xs", None)
            ys = kwargs.pop("ys", None)

            # Remember the raw data so the series can be rebuilt from scratch at
            # render time (only `ys` triggers a data change; a lone `xs` is
            # ignored, matching the documented streaming contract).
            if has_ys:
                if copy:
                    xs = _defensive_copy(xs)
                    ys = _defensive_copy(ys)
                self._raw_xs = xs
                self._raw_ys = ys

            # Pin any explicitly-passed bounds; accumulate all other options.
            # Option values are snapshotted too: several (e.g. `lines`, `color`,
            # `legend_labels`, gridlines) are mutable lists, and a producer that
            # mutates one after the call could otherwise desync it from the
            # series count and crash the deferred render -- the same race as for
            # `xs`/`ys`. Scalars/strings pass through `_defensive_copy` untouched.
            for k, v in kwargs.items():
                if copy:
                    v = _defensive_copy(v)
                if k in _BOUND_KEYS:
                    self._pinned_bounds.add(k)
                    self._pending_bound_values[k] = v
                else:
                    self._option_kwargs[k] = v

            self._dirty = True

    def _recompute(self) -> None:
        """
        Rebuild the series from the raw data and recompute `self.options` from
        the accumulated options and pinned bounds. The caller must hold
        `self._lock`. This is the expensive part of an update.
        """
        # Nothing to plot yet: keep default options and defer until data arrives
        # (this also makes a style-only update on an empty plot a no-op instead
        # of an error).
        if self._raw_ys is None:
            self._dirty = False
            return

        # Always rebuild a fresh series from the raw data, so the validator's
        # in-place transforms (e.g. log scaling) are applied exactly once and
        # never compounded across repeated renders.
        previous = self.series
        series = MultiSeries(xs=self._raw_xs, ys=self._raw_ys)
        if len(series) == 0:
            self.series = series
            self._dirty = False
            return

        # If the data type of an axis flipped (e.g. float <-> datetime), any
        # pinned bound on that axis is now in the wrong numeric space and must be
        # dropped so it auto-ranges in the new space. Bounds supplied explicitly
        # since the last recompute are kept.
        explicit = self._pending_bound_values
        pinned_bounds = self._pinned_bounds.copy()
        if series.x_is_time_series != previous.x_is_time_series or (
            (series.x_timezone is None) != (previous.x_timezone is None)
        ):
            pinned_bounds -= {"x_min", "x_max"} - set(explicit)
        if series.y_is_time_series != previous.y_is_time_series or (
            (series.y_timezone is None) != (previous.y_timezone is None)
        ):
            pinned_bounds -= {"y_min", "y_max"} - set(explicit)

        # Build the kwargs for the validator: persisted options + pending
        # explicit bounds + re-injected pinned bounds. Re-injected bounds come
        # from `self.options` and are therefore already in plot space, so the
        # validator must not transform them again.
        merged: dict = dict(self._option_kwargs)
        merged.update(explicit)
        reinjected = set()
        for b in pinned_bounds:
            if b not in merged:
                merged[b] = getattr(self.options, b)
                reinjected.add(b)

        options = validate_and_transform_options(
            series=series,
            kwargs=merged,
            bounds_already_in_plot_space=frozenset(reinjected),
        )
        self.series = series
        self.options = options
        self._pinned_bounds = pinned_bounds
        self._pending_bound_values = {}
        self._dirty = False

    def _render(self, max_width: int | None = None) -> str:
        """
        The single render path: turn the current state into the plot string,
        without printing, erasing, or permanently mutating the options. Applies
        any pending data/options first (see `_recompute`).

        If `max_width` is given (i.e. when rendered by Rich), the plot fills the
        allocated width: the total line length is capped to `max_width` via the
        existing `line_length_hard_cap` mechanism, and -- unless the user set an
        explicit `width` -- the plot region also grows to fill it, the way Rich
        renderables normally fill their container. An explicit `width` is
        respected (only shrunk if the container is narrower).
        """
        with self._lock:
            if self._dirty:
                self._recompute()
            opts = self.options
            saved_cap = opts.line_length_hard_cap
            saved_width = opts.width
            saved_initial_width = opts._initial_width
            try:
                if max_width is not None:
                    opts.line_length_hard_cap = (
                        max_width if saved_cap is None else min(saved_cap, max_width)
                    )
                    # Grow to fill the allocated width when the user did not pick
                    # a width. Overshooting and letting the hard-cap logic trim
                    # makes the plot fit `max_width` exactly (accounting for
                    # borders and axis labels).
                    if "width" not in self._option_kwargs:
                        opts.width = max_width
                        opts._initial_width = max_width
                (
                    x_axis_labels,
                    y_axis_labels,
                    pixel_character_matrix,
                ) = sections.generate_body_raw_elements(self.series, opts)
                header_buffer = sections.generate_header(opts)
                body_buffer = sections.generate_body(
                    x_axis_labels, y_axis_labels, pixel_character_matrix, opts
                )
                return "\n".join(header_buffer + body_buffer)
            finally:
                # Restore the options to their pre-render state. The cap logic in
                # `sections` mutates `width`, so restore all three.
                opts.line_length_hard_cap = saved_cap
                opts._initial_width = saved_initial_width
                opts.width = saved_width

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        """
        Rich renderable protocol. Allows `console.print(plot_gen(ys=...))` and
        embedding plots in Rich containers such as `Panel`, `Group`, `Columns`.

        Requires the optional `rich` dependency: `pip install uniplot[rich]`.
        """
        try:
            from rich.text import Text
        except ImportError as e:  # pragma: no cover - exercised via monkeypatch
            raise ImportError(
                "Rich integration requires the 'rich' package. "
                "Install it with:  pip install uniplot[rich]"
            ) from e

        plot_string = self._render(max_width=options.max_width)
        # `from_ansi` parses uniplot's ANSI color codes into native Rich styling,
        # so colors are preserved and no raw escape sequences leak into output.
        yield Text.from_ansi(plot_string)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        """
        Report the plot's width to Rich so layouts (e.g. `Columns`, tables) can
        size it correctly.
        """
        from rich.measure import Measurement

        plot_string = self._render(max_width=options.max_width)
        widths = [
            len(colors.COLOR_CODE_REGEX.sub("", line))
            for line in plot_string.split("\n")
        ]
        natural = max(widths) if widths else 0
        return Measurement(min(natural, options.max_width), natural)


def plot_to_string(ys: Any, xs: Any | None = None, **kwargs) -> str:
    """
    Same as `plot`, but the return type is string. Ignores the `interactive`
    option.

    Can be used to integrate uniplot in other applications, or if the output is
    desired to be not stdout.
    """
    return plot_gen(xs=xs, ys=ys, **kwargs).to_string()


#####################################
# Experimental features, see Readme #
#####################################


def histogram(
    xs: Any,
    bins: int = 20,
    bins_min: float | None = None,
    bins_max: float | None = None,
    **kwargs,
) -> None:
    """
    Plot a histogram to the terminal.

    Parameters:

    - `xs` are the values of the points to plot. This parameter is mandatory
      and can either be a list or a list of lists, or the equivalent NumPy
      array.
    - Any additional keyword arguments are passed to the
      `uniplot.options.Options` class.
    """
    # HACK Use the `MultiSeries` constructor to cast values to uniform format
    multi_series = MultiSeries(ys=xs)
    xs_histo, ys_histo = elements.prepare_histogram(
        multi_series, bins, bins_min, bins_max
    )

    # Histograms usually make sense only with lines
    kwargs["lines"] = True
    plot(xs=xs_histo, ys=ys_histo, **kwargs)


def histogram_to_string(
    xs: Any,
    bins: int = 20,
    bins_min: float | None = None,
    bins_max: float | None = None,
    **kwargs,
) -> str:
    """
    Same as `histogram`, but the return type is string. Ignores the `interactive`
    option.

    Can be used to integrate uniplot in other applications, or if the output is
    desired to be not stdout.
    """
    # HACK Use the `MultiSeries` constructor to cast values to uniform format
    multi_series = MultiSeries(ys=xs)
    xs_histo, ys_histo = elements.prepare_histogram(
        multi_series, bins, bins_min, bins_max
    )

    # Histograms usually make sense only with lines
    kwargs["lines"] = True
    return plot_to_string(xs=xs_histo, ys=ys_histo, **kwargs)


def sparkline(
    ys: Any,
    width: int = 5,
    *,
    color: Any = None,
    y_min: Any = None,
    y_max: Any = None,
) -> None:
    """Print a filled Braille sparkline with optional color and fixed y bounds."""
    print(sparkline_to_string(ys, width=width, color=color, y_min=y_min, y_max=y_max))


def sparkline_to_string(
    ys: Any,
    width: int = 5,
    *,
    color: Any = None,
    y_min: Any = None,
    y_max: Any = None,
) -> str:
    """Return the same chart as `sparkline`, without a trailing newline.

    Color uses the standard plot color formats. None uses the plot default.
    Each y bound defaults to automatic scaling when None.
    """
    options = {
        key: value
        for key, value in {"color": color, "y_min": y_min, "y_max": y_max}.items()
        if value is not None
    }
    return plot_to_string(
        ys,
        width=width,
        height=1,
        border=None,
        fill="bottom",
        lines=True,
        x_labels=False,
        y_labels=False,
        x_gridlines=[],
        y_gridlines=[],
        character_set="braille",
        **options,
    )


###########
# private #
###########


def _defensive_copy(value: Any) -> Any:
    """
    Return a private copy of a value that is immune to later in-place mutation
    or appends by the producer. Used for both the `xs`/`ys` data and for
    mutable option values (e.g. `lines`, `color`, `legend_labels`, gridlines).

    This is what makes `plot_gen.set_data` safe to call with live, still-growing
    lists while `rich.live.Live` renders on another thread: we capture the value
    at call time (synchronously, on the producer's own thread), so the producer
    cannot desync it between the call and the deferred render (see `set_data`).

    The copy is intentionally shallow/structural -- an O(n) memcpy for arrays,
    one level deep for sequences -- so it stays cheap (at 1M points: ~0.15 ms
    for a NumPy array, ~2 ms for a Python list). The expensive cast/validation
    remains deferred to `_recompute`. Immutable scalars/strings (and anything we
    cannot cheaply copy) pass through unchanged.
    """
    if value is None:
        return None
    # NumPy array (incl. an N-D multi-series block): one copy captures it all.
    if isinstance(value, np.ndarray):
        return value.copy()
    # Generic sequence. Copy one level deep so that, in the multi-series case,
    # an append to a live *inner* list cannot desync x/y lengths at render time.
    if isinstance(value, (list, tuple)):
        return [
            row.copy()
            if isinstance(row, np.ndarray)
            else row[:]
            if isinstance(row, (list, tuple))
            else row
            for row in value
        ]
    # Anything else with a value-preserving `.copy()` (e.g. a pandas
    # Series/DataFrame): use it to keep dtype and index intact.
    copy_method = getattr(value, "copy", None)
    if callable(copy_method):
        try:
            return copy_method()
        except (TypeError, ValueError):
            # An unusable `.copy()`; fall back to the value itself.
            return value
    return value
