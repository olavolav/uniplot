# Uniplot
[![Build Status](https://github.com/olavolav/uniplot/actions/workflows/unit_tests.yml/badge.svg?branch=master)](https://github.com/olavolav/uniplot/actions?query=workflow%3A"Unit+Tests")
[![PyPI Version](https://badge.fury.io/py/uniplot.svg)](https://pypi.org/project/uniplot/)
[![PyPI Downloads](https://pepy.tech/badge/uniplot)](https://pepy.tech/project/uniplot)

Lightweight plotting to the terminal. 4x resolution via Unicode.

![uniplot demo GIF](https://github.com/olavolav/uniplot/raw/master/resource/uniplot-demo.gif)

When working with production data science code it can be handy to have a
plotting tool that does not rely on graphics dependencies or works only in a
Jupyter notebook.

There are two main use cases:

1. **ML / data science CI/CD pipelines** — when something goes wrong, you get
   not only the error and backtrace but also plots that show what the problem
   was.
2. **AI coding agents like [Claude Code](https://claude.com/claude-code)** —
   uniplot output is plain terminal text, which works in both directions: the
   agent can render plots back to you as visual feedback inside its response
   (e.g. summarising a parameter scan across pipeline runs, or showing how a
   return variable changes), and it can also read its own plots to reason
   about shapes, trends and outliers. With `uv` no install step is needed:
   ```shell
   uv run --with uniplot python -c "from uniplot import plot; ys = [1, 4, 16]; plot(ys)"
   ```


## Features

* Unicode drawing, so 4x the resolution (pixels) of usual ASCII plots, or even
  8x when using Braille characters
* Super simple API
* Interactive mode (pass `interactive=True`)
* Color mode (pass `color=True`) useful in particular when plotting multiple series
* Works directly with the data ecosystem you already use:
  [NumPy](https://numpy.org), [pandas](https://pandas.pydata.org) and
  [Polars](https://pola.rs)
* Integrates with [Rich](https://github.com/Textualize/rich): embed plots in panels,
  columns and live-updating dashboards (see below)
* It's fast: Plotting 1M data points takes 26ms thanks to NumPy magic

Please note that Unicode drawing will work correctly only when using a font
that fully supports the [Block Elements character
set](https://en.wikipedia.org/wiki/Box-drawing_character) or the [Braille
character set](https://en.wikipedia.org/wiki/Braille_Patterns). Please refer to
[this page for a (incomplete) list of supported
fonts](https://www.fileformat.info/info/unicode/block/block_elements/fontsupport.htm)
and the options below to select the character set.


## Simple example


```python
import math

x = [math.sin(i / 20) + i / 300 for i in range(600)]
from uniplot import plot

plot(x, title="Sine wave")
```

Result:
```
                          Sine wave
┌────────────────────────────────────────────────────────────┐
│                                                    ▟▀▚     │
│                                                   ▗▘ ▝▌    │
│                                       ▗▛▜▖        ▞   ▐    │
│                                       ▞  ▜       ▗▌    ▌   │ 2
│                           ▟▀▙        ▗▘  ▝▌      ▐     ▜   │
│                          ▐▘ ▝▖       ▞    ▜      ▌     ▝▌  │
│              ▗▛▜▖        ▛   ▜      ▗▌    ▝▌    ▐▘      ▜  │
│              ▛  ▙       ▗▘   ▝▖     ▐      ▚    ▞       ▝▌ │
│  ▟▀▖        ▐▘  ▝▖      ▟     ▚     ▌      ▝▖  ▗▌        ▜▄│ 1
│ ▐▘ ▐▖       ▛    ▙      ▌     ▐▖   ▗▘       ▚  ▞           │
│ ▛   ▙      ▗▘    ▐▖    ▐       ▙   ▞        ▝▙▟▘           │
│▐▘   ▐▖     ▐      ▌    ▛       ▐▖ ▗▘                       │
│▞     ▌     ▌      ▐   ▗▘        ▜▄▛                        │
│▌─────▐────▐▘───────▙──▞────────────────────────────────────│ 0
│       ▌   ▛        ▝▙▟▘                                    │
│       ▜  ▐▘                                                │
│        ▙▄▛                                                 │
└────────────────────────────────────────────────────────────┘
         100       200       300       400       500       600
```

For more examples, please see the `examples/` folder.


## Parameters

The `plot` function accepts a number of parameters, all listed below. Note that
only `ys` is required, all others are optional.

There is also a `plot_to_string` function with the same signature, if you want
the result as a list of strings, to include the output elsewhere. The only
difference is that `plot_to_string` does not support interactive mode.


### Data

* `xs` - The x coordinates of the points to plot. Can either be `None`, or a
  list or NumPy array for plotting a single series, or a list of those for
  plotting multiple series. Defaults to `None`, meaning that the x axis will be
  just the sample index of `ys`.
* `ys` - The y coordinates of the points to plot. Can either be a list or NumPy
  array for plotting a single series, or a list of those for plotting multiple
  series.

In both cases, NaN or `None` values are ignored.

Note that since v0.12.0 you can also pass a list or an NumPy array of
timestamps, and the axis labels should be formatted correctly.


### Options

In alphabetical order:

#### Basic options

* `color` - Draw series in color. Defaults to `False` when plotting a single
  series, and to `True` when plotting multiple. Also accepts a list of colors,
  identified by strings like `"red"` for simple ANSI colors, tuples of RGB
  values like `(255,0,0)`, or hexadecimal RGB colors like `"#B4FBB8"`.
  Alternaively, you can specify a color theme as a string, as defined in
  `uniplot/color_themes.py`. Note that for RGB colors you need to use a
  terminal that supports them.
* `height` - The height of the plotting region, in characters. Default is `17`.
* `interactive` - Enable interactive mode. Defaults to `False`.
* `legend_labels` - Labels for the series. Can be `None` or a list of strings.
  Defaults to `None`.
* `lines` - Enable lines between points. Can either be `True` or `False`, or a
  list of Boolean values for plotting multiple series. Defaults to `False`.
* `title` - The title of the plot. Defaults to `None`.
* `width` - The width of the plotting region, in characters. Default is `60`.
  Note that if the `line_length_hard_cap` option (see "Advanced options" below)
  is used and there is not enough space, the actual width may be smaller.
* `x_max` - Maximum x value of the view. Defaults to a value that shows all
  data points.
* `x_min` - Minimum x value of the view. Defaults to a value that shows all
  data points.
* `x_unit` - Unit of the x axis. This is a string that is appended to the axis
  labels. Defaults to `""`.
* `y_max` - Maximum y value of the view. Defaults to a value that shows all
  data points.
* `y_min` - Minimum y value of the view. Defaults to a value that shows all
  data points.
* `y_unit` - Unit of the y axis. This is a string that is appended to the axis
  labels. Defaults to `""`.

#### Advanced options

* `character_set` - Which Unicode character set to use. Use `"block"` for
  the [Block Elements character
  set](https://en.wikipedia.org/wiki/Block_Elements) with 4x resolution, or
  `"braille"` for the [Braille character
  set](https://en.wikipedia.org/wiki/Braille_Patterns) with 8x resolution,
  `"ascii"` to use ASCII characters only. Braille has the highest resolution,
  and a lighter look overall. Defaults to `"block"`.
* `fill` - Fill the area between adjacent samples and a baseline. Defaults to
  `None` (disabled). Use a number such as `0`, `"bottom"` for the current view's
  bottom edge, or a list with one setting per series, such as `[0, None]`.
  Fill uses the series color and connects samples independently of `lines`.
  Missing or infinite samples leave gaps, and isolated points have no filled
  area. Overlapping segment areas are combined, including paths that reverse
  direction. Any positive-area pixel overlap is filled, preserving narrow peaks.
  Explicit baselines participate in automatic y bounds; explicit view bounds
  still take precedence. Logarithmic y axes require a positive baseline.
  Datetime y axes accept datetime baselines or numeric Unix timestamps in
  seconds. Boolean values are rejected.
* `force_ascii_characters` -  List of characters to use when using the
  ASCII character set. Defaults to `["+", "x", "o", "*", "~", "."]`.
* `legend_placement` - Arrangement of the legend labels. `"auto"` attempts to
  place them one or more rows next to each other, while `"vertical"` is a
  block with one label per row. Defaults to `"auto"`.
* `line_length_hard_cap` - Enforce a hard limit on the number of characters per
  line of the plot area. This may override the `width` option if there is not
  enough space. Defaults to `None`.
* `border` - Frame around the plot area. Use `"box"` for square corners
  (the default), `"rounded"` for rounded corners, or `None` to hide the frame.
* `rounded_corners` - Deprecated. Use `border="rounded"` instead. Removal is
  planned no earlier than May 14, 2027. If `True`, a `"box"` border has rounded
  corners. Defaults to `False`.
* `x_as_log` - Plot the x axis as logarithmic scale. Defaults to `False`.
* `x_gridlines` - A list of x values that have a vertical line for better
  orientation. Defaults to `[0]`, or to `[]` if `x_as_log` is enabled.
* `x_gridlines_color` - A boolean or a list of colors for the vertical
  gridlines, as specified above for the `color` option. Defaults to `False`.
* `x_labels` - Enable axis labels for the x axis. Defaults to `True`.
* `x_unit_scaling` - Scale the x axis labels, assuming `x_unit` is the base
  unit. Supported values are `""` (no scaling) and `"si"` (SI prefixes `k`, `M`,
  `G`, … and `m`, `µ`, `n`, …). For example, with `x_unit=" m"` a label of `1000`
  is shown as `1 km` and `0.003` as `3 mm`. The prefix is inserted before the
  first non-whitespace character of the unit (so a leading space is preserved),
  and a blank unit still gets a prefix (e.g. `200k`). Defaults to `""`.
* `y_as_log` - Plot the y axis as logarithmic scale. Defaults to `False`.
* `y_gridlines` - A list of y values that have a horizontal line for better
  orientation. Defaults to `[0]`, or to `[]` if `y_as_log` is enabled.
* `y_gridlines_color` - A boolean or a list of colors for the horizontal
  gridlines, as specified above for the `color` option. Defaults to `False`.
* `y_labels` - Enable axis labels for the y axis. Defaults to `True`.
* `y_unit_scaling` - Scale the y axis labels, assuming `y_unit` is the base
  unit. See `x_unit_scaling`. Defaults to `""`.


### Changing default parameters

uniplot does not store a state of the configuration parameters. However, you
can define a new plot funtion with new defaults by defining a `partial`. See
the following example:

```python
from functools import partial
from uniplot import plot as default_plot

plot = partial(default_plot, height=25, width=80)
```

This defines a new `plot` function that is identical to the original, except
the default values for `width` and `height` are now different.


## Experimental features

### Plotting histograms

For convenience there is also a `histogram` function that accepts one or more
series and plots bar-chart like histograms. It will automatically discretize
the series into a number of bins given by the `bins` option and display the
result.

Additional options, in alphabetical order:

* `bins` - Number of bins to use. Defaults to `20`.
* `bins_min` - Lower limit of the first bin. Defaults to the minimum of the
  series.
* `bins_max` - Upper limit of the last bin. Defaults to the maximum of the
  series.

When calling the `histogram` function, the `lines` option is `True` by default.

Example:

```python
import numpy as np

x = np.sin(np.linspace(1, 1000))
from uniplot import histogram

histogram(x)
```

Result:
```
┌────────────────────────────────────────────────────────────┐
│   ▛▀▀▌                       │                   ▐▀▀▜      │ 5
│   ▌  ▌                       │                   ▐  ▐      │
│   ▌  ▌                       │                   ▐  ▐      │
│   ▌  ▀▀▀▌                    │                ▐▀▀▀  ▝▀▀▜   │
│   ▌     ▌                    │                ▐        ▐   │
│   ▌     ▌                    │                ▐        ▐   │
│   ▌     ▙▄▄▄▄▄▖              │          ▗▄▄▄  ▐        ▐   │
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜  ▐▀▀▀  ▝▀▀▀        ▐   │
│   ▌                          │    ▐  ▐                 ▐   │
│   ▌                          │    ▐  ▐                 ▐   │
│   ▌                          │    ▐▄▄▟                 ▐   │
│   ▌                          │                         ▐   │
│   ▌                          │                         ▐   │
│▄▄▄▌▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁│▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▐▄▄▄│ 0
└────────────────────────────────────────────────────────────┘
     -1                        0                       1
```

### Sparklines

Use `sparkline` to print a one-line Braille chart with connected points.

```python
from uniplot import sparkline

sparkline([1, 3, 2, 5, 4], width=10)
```

Use `sparkline_to_string(ys, width=5)` to return the chart as a string.
Both helpers fill to the bottom of the view and accept keyword-only `color`,
`y_min`, and `y_max`. Color uses the standard plot color formats. Set y bounds
to compare several sparklines on the same scale; omitted bounds scale automatically.

```python
sparkline([10, 30, 20], width=20, color=["green"], y_min=0, y_max=100)
```

### Arrow keys and FPS-style keys

In interactive mode, we now also support wasd or FPS-style keyboard layout and
the arrow keys. Arrows should work on most platforms like Mac, Linux or Windows. We might make the keyboard layout fully configurable, to change the current Vim-inspired one, at a later date. For now, you have 3 ways to move the view:

* Vim-style: `h` left, `j` down, `k` up, `l` right, `u` zoom in, `n` zoom out.
* FPS-style: `a` left, `s` down, `w` up, `d` right, `]` zoom in, `[` zoom out.
* Arrow keys: movement obvious, `]` zoom in, `[` zoom out.


### Streaming

There is support for streaming using the `plot_gen` class. It wraps the plot
function and holds the plotting state, so you can `update` it with new data and
have it re-drawn in place.

Example, assuming we had a function called `get_new_data` to get new data from
some source:
```python3
from uniplot import plot_gen

plt = plot_gen()
ys = []

while True:
    ys.append(get_new_data())
    plt.update(ys=ys, title=f"Streaming: {len(ys)} data point(s) ...")
```

Each `update()` re-draws from the current state. Any bound you set explicitly
(e.g. `y_min=-1, y_max=1`) — or via interactive pan/zoom — is *pinned* and kept
across updates, while all other bounds keep auto-ranging to fit the new data.
Other options (such as `title`, `color`, `lines`) persist across updates too, so
you only need to pass them once.

`update()` returns the rendered string as well. If you only want the string (no
printing), use `plt.to_string()` or the `plot_to_string()` function.

See `examples/5-streaming.py` for a more complete example.


## Rich integration

uniplot plots are [Rich](https://github.com/Textualize/rich) renderables. Pass a
`plot_gen` object straight to a Rich `Console`, or embed it in any Rich
container such as `Panel`, `Group` or `Columns`. Colors are preserved and the
plot fits the width Rich allocates, so it sits cleanly inside layouts and
dashboards.

```python
from rich.console import Console
from rich.panel import Panel
from uniplot import plot_gen

console = Console()

# Print a plot directly ...
console.print(plot_gen(ys=[1, 2, 4, 3], title="My plot"))

# ... or embed it in any Rich container.
console.print(Panel(plot_gen(ys=[1, 2, 4, 3]), title="Wrapped in Rich"))
```

This makes uniplot a natural fit for Rich-based CLIs, monitoring dashboards and
agent tooling. Rich is an optional dependency — install it with:

```shell
pip install uniplot[rich]
```

See `examples/10-rich_integration.py` for a fuller demo including colored
multi-series plots and a multi-column layout.

#### Live updates

For a smoothly updating display, drive a plot with `rich.live.Live`. Feed new
data with the thread-safe `set_data()` (which updates state without printing)
and let Rich re-render on its own schedule. A fast producer and a slower refresh
rate decouple cleanly — updates between two refreshes simply coalesce into one
render. `set_data()` snapshots the data and options you pass, so it is safe to
hand over a live, still-growing list even while Rich renders on another thread
(pass `copy=False` to skip the snapshot if you already supply fresh objects each
call):

```python
import math, time
from rich.live import Live
from uniplot import plot_gen

plt = plot_gen(lines=True, y_min=-1.2, y_max=1.2, title="Live sine")
ys = []
with Live(plt, refresh_per_second=10) as live:
    for i in range(400):
        ys.append(math.sin(i / 10))
        plt.set_data(ys=ys[-100:])  # high-rate updates; no printing
        time.sleep(0.005)
```

See `examples/11-rich_live.py`.


## Installation

Install via pip using:

```shell
pip install uniplot
```

For faster line rendering with very large datasets (1M+ points), install the optional Numba dependency:

```shell
pip install uniplot[fast]
```

Note: the first plot after installation (or after a Numba/Python upgrade) will take a few extra seconds to compile — subsequent calls reuse a disk cache and are fast.

For the [Rich](https://github.com/Textualize/rich) integration, install the optional Rich dependency:

```shell
pip install uniplot[rich]
```


## Contributing

Clone this repository, and make sure you
[have uv installed](https://docs.astral.sh/uv/getting-started/installation/).

On most Linux-like systems like MacOS you can run:
```shell
make
```
See the `Makefile` for details and more granular commands.

Alternatively, on systems like Windows that do not have `make` installed, you can run:
```shell
uv run scripts/run_tests.sh
```

Then proceed with issues, PRs etc. the usual way.


## Projects that use uniplot

* The [Photovoltaic Geographic Information System (PVGIS)](https://code.europa.eu/pvgis/pvgis)
  uses uniplot to [generate horizon plots](https://asciinema.org/a/pynlwepKNRE6gqKqwPr6JmzTP).
* The [FlexMeasures] CLI uses uniplot to [plot beliefs in sensors](https://github.com/FlexMeasures/flexmeasures/blob/2e3680cb35c1a4f2b94c7f77f9eb2ff70760755e/flexmeasures/cli/data_show.py#L754) for smart power control.

You can find many more in the [Dependency Graph](https://github.com/olavolav/uniplot/network/dependents).
