# Uniplot
[![Build Status](https://github.com/olavolav/uniplot/workflows/Unit%20Tests/badge.svg)](https://github.com/olavolav/uniplot/actions?query=workflow%3A"Unit+Tests")
[![PyPI Version](https://badge.fury.io/py/uniplot.svg)](https://pypi.org/project/uniplot/)
[![PyPI Downloads](https://pepy.tech/badge/uniplot)](https://pepy.tech/project/uniplot)

Lightweight plotting to the terminal. 4x resolution via Unicode.

![uniplot demo GIF](https://github.com/olavolav/uniplot/raw/master/resource/uniplot-demo.gif)

When working with production data science code it can be handy to have plotting
tool that does not rely on graphics dependencies or works only in a Jupyter
notebook.

The **use case** that this was built for is to have plots as part of your data
science / machine learning CI/CD pipeline - that way whenever something goes
wrong, you get not only the error and backtrace but also plots that show what
the problem was.


## Features

* Unicode drawing, so 4x the resolution (pixels) of usual ASCII plots
* Super simple API
* Interactive mode (pass `interactive=True`)
* Color mode (pass `color=True`) useful in particular when plotting multiple series
* It's fast: Plotting 1M data points takes 100ms thanks to NumPy magic
* Only one dependency: NumPy (but you have that anyway don't you)

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
x = [math.sin(i/20)+i/300 for i in range(600)]
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
  series, and to `True` when plotting multiple. Also accepts a list of strings,
  to modify the default order of
  `["blue", "magenta", "green", "yellow", "cyan", "red"]`.
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

* `callback_keypressed` - Callback function that is used when a key is pressed
  in interactive mode with arguments `(options, key_pressed)`. Defaults to the
  `_default_callback_keypressed` function defined in `uniplot/options.py`. Note
  that interactive mode will end if the callback function returns a value that
  evaluates to false.
* `character_set` - Which Unicode character set to use. Use `"block"` for
  the [Block Elements character
  set](https://en.wikipedia.org/wiki/Block_Elements) with 4x resolution, or
  `"braille"` for the [Braille character
  set](https://en.wikipedia.org/wiki/Braille_Patterns) with 8x resolution.
  The latter has a lighter look overall. Defaults to `"block"`.
* `force_ascii` - Force ASCII characters for plotting only. This can be useful
  for compatibility, for example when using uniplot inside of CI/CD systems
  that do not support Unicode. Defaults to `False`.
* `force_ascii_characters` -  List of characters to use when plotting in
  `force_ascii` mode. Default to `["+", "x", "o", "*", "~", "."]`.
* `line_length_hard_cap` - Enforce a hard limit on the number of characters per
  line of the plot area. This may override the `width` option if there is not
  enough space. Defaults to `None`.
* `x_as_log` - Plot the x axis as logarithmic scale. Defaults to `False`.
* `x_gridlines` - A list of x values that have a vertical line for better
  orientation. Defaults to `[0]`, or to `[]` if `x_as_log` is enabled.
* `y_as_log` - Plot the y axis as logarithmic scale. Defaults to `False`.
* `y_gridlines` - A list of y values that have a horizontal line for better
  orientation. Defaults to `[0]`, or to `[]` if `y_as_log` is enabled.


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

### Streaming

There is initial support for streaming using the `plot_gen` function. The idea
is have a class that wraps the plot function and the state of plotting, such
that we can `update` the state of the plot.

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

See `examples/5-sreaming.py` for a more complete example.


## Installation

Install via pip using:

```sh
pip install uniplot
```


## Contributing

Clone this repository, and install dependecies via `poetry install`.

You can run the tests via `poetry run ./run_tests` to make sure your setup is
good. Then proceed with issues, PRs etc. the usual way.
