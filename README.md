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
science / machine learning CI/cd pipeline - that way whenever something goes
wrong, you get not only the error and backtrace but also plots that show what
the problem was.


## Features

* Unicode drawing, so 4x the resolution (pixels) of usual ASCII plots
* Super simple API
* Interactive mode (pass `interactive=True`)
* Color mode (pass `color=True`) useful in particular when plotting multiple series
* It's fast: Plotting 1M data points takes 100ms thanks to NumPy magic
* Only one dependency: NumPy (but you have that anyway don't you)

Please note that Unicode drawing will work correctly only when using a font that
fully supports the [Box-drawing character set](https://en.wikipedia.org/wiki/Box-drawing_character).
Please refer to [this page for a (incomplete) list of supported fonts](https://www.fileformat.info/info/unicode/block/block_elements/fontsupport.htm).


## Examples

Note that all the examples are without color and plotting only a single series of data.
For using color see the GIF example above.

### Plot sine wave

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

### Plot global temperature data

Here we are using Pandas to load and prepare global temperature data from the [Our World
in Data GitHub repository](https://github.com/owid/owid-datasets).

First we load the data, rename a column and and filter the data:

```python
import pandas as pd
uri = "https://github.com/owid/owid-datasets/raw/master/datasets/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre.csv"
data = pd.read_csv(uri)
data = data.rename(columns={"Global average temperature anomaly (Hadley Centre)": "Global"})
data = data[data.Entity == "median"]
```

Then we can plot it:

```python
from uniplot import plot
plot(xs=data.Year, ys=data.Global, lines=True, title="Global normalized land-sea temperature anomaly", y_unit=" °C")
```

Result:
```
        Global normalized land-sea temperature anomaly
┌────────────────────────────────────────────────────────────┐
│                                                          ▞▀│
│                                                         ▐  │
│                                                         ▐  │
│                                                     ▗   ▌  │ 0.6 °C
│                                           ▙  ▗▄ ▛▄▖▗▘▌ ▞   │
│                                          ▗▜  ▌ ▜  ▚▞ ▚▞    │
│                                          ▐▝▖▐      ▘       │
│                                    ▗   ▗ ▌ ▙▌              │ 0.3 °C
│                                    ▛▖  ▞▙▘  ▘              │
│                              ▖  ▗▄▗▘▐ ▐▘▜                  │
│                            ▟ █  ▞ ▜ ▝▄▘                    │
│   ▗▚   ▗    ▖       ▗   ▖▗▞ █▐  ▌    ▘                     │
│▁▁▁▞▐▁▁▗▘▜▗▀▀▌▁▁▁▁▙▁▁▟▁▁▁▙▐▁▁▜▁▌▞▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁│ 0 °C
│▚ ▐ ▝▖ ▐  ▛  ▌ ▗▄▐ ▌▗▘▌ ▐▝▌    ▝▘                           │
│ ▌▌  ▌ ▞     ▐▗▘ ▛ ▐▞ ▌ ▐                                   │
│ ▝   ▝▖▌     ▐▞    ▝▌ ▚▜▐                                   │
│      ▗▌     ▝        ▝ ▌                                   │
└────────────────────────────────────────────────────────────┘
1,950    1,960    1,970   1,980    1,990    2,000   2,010
```


## Parameters

The `plot` function accepts a number of parameters, all listed below. Note that
only `ys` is required, all others are optional.

There is also a `plot_to_string` function with the same signature, if you want
the result as a list of strings, to include the output elsewhere.

### Data

* `xs` - The x coordinates of the points to plot. Can either be `None`, or a
  list or NumPy array for plotting a single series, or a list of those for
  plotting multiple series. Defaults to `None`, meaning that the x axis will be
  just the sample index of `ys`.
* `ys` - The y coordinates of the points to plot. Can either be a list or NumPy
  array for plotting a single series, or a list of those for plotting multiple
  series.

In both cases, NaN values are ignored.

Note that since v0.12.0 you can also pass a list or an NumPy array of
timestamps, and the axis labels should be formatted correctly. Limitations see
below.


### Options

In alphabetical order:

* `color` - Draw series in color. Defaults to `False` when plotting a single series, and to `True` when plotting multiple.
* `force_ascii` - Force ASCII characters for plotting only. This can be useful for compatibility, for example when using uniplot inside of CI/CD systems that do not support Unicode. Defaults to `False`.
* `height` - The height of the plotting region, in characters. Default is `17`.
* `interactive` - Enable interactive mode. Defaults to `False`.
* `legend_labels` - Labels for the series. Can be `None` or a list of strings. Defaults to `None`.
* `lines` - Enable lines between points. Can either be `True` or `False`, or a list of those values for plotting multiple series. Defaults to `False`.
* `line_length_hard_cap` - Enforce a hard limit on the number of characters per line of the plot area. This may override the `width` option if there is not enough space. Defaults to `None`.
* `title` - The title of the plot. Defaults to `None`.
* `width` - The width of the plotting region, in characters. Default is `60`. Note that if the `line_length_hard_cap` option is used and there is not enough space, the actual width may be smaller.
* `x_as_log` - Plot the x axis as logarithmic scale. Defaults to `False`.
* `x_gridlines` - A list of x values that have a vertical line for better orientation. Defaults to `[0]`, or to `[]` if `x_as_log` is enabled.
* `x_max` - Maximum x value of the view. Defaults to a value that shows all data points.
* `x_min` - Minimum x value of the view. Defaults to a value that shows all data points.
* `x_unit` - Unit of the x axis. This is a string that is appended to the axis labels. Defaults to `""`.
* `y_as_log` - Plot the y axis as logarithmic scale. Defaults to `False`.
* `y_gridlines` - A list of y values that have a horizontal line for better orientation. Defaults to `[0]`, or to `[]` if `y_as_log` is enabled.
* `y_max` - Maximum y value of the view. Defaults to a value that shows all data points.
* `y_min` - Minimum y value of the view. Defaults to a value that shows all data points.
* `y_unit` - Unit of the y axis. This is a string that is appended to the axis labels. Defaults to `""`.

### Changing default parameters

uniplot does not store a state of the configuration parameters. However, you can define a
new plot funtion with new defaults by defining a `partial`:

```python
from functools import partial
from uniplot import plot as default_plot
plot = partial(default_plot, height=25, width=80)
```

This defines a new `plot` function that is identical to the original, except the default
values for `width` and `height` are now different.


## Experimental features

### Plotting histograms

For convenience there is also a `histogram` function that accepts one or more
series and plots bar-chart like histograms. It will automatically discretize
the series into a number of bins given by the `bins` option and display the
result.

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
│   ▌  ▀▀▀▌                    │                ▐▀▀▀  ▝▀▀▜   │ 4
│   ▌     ▌                    │                ▐        ▐   │
│   ▌     ▌                    │                ▐        ▐   │
│   ▌     ▙▄▄▄▄▄▖              │          ▗▄▄▄  ▐        ▐   │ 3
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▌              │          ▐  ▐  ▐        ▐   │
│   ▌           ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜  ▐▀▀▀  ▝▀▀▀        ▐   │ 2
│   ▌                          │    ▐  ▐                 ▐   │
│   ▌                          │    ▐  ▐                 ▐   │
│   ▌                          │    ▐▄▄▟                 ▐   │ 1
│   ▌                          │                         ▐   │
│   ▌                          │                         ▐   │
│▄▄▄▌▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁│▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▐▄▄▄│ 0
└────────────────────────────────────────────────────────────┘
     -1                        0                       1
```

### Plotting time series

There is inital support for using timestamps for the axis labels. It should work with most formats.

Missing so far are nicer axis labels for time stamps, as well as timezone support.

Example:

```python
import numpy as np
dates =  np.arange('2024-02-17T12:10', 4*60, 60, dtype='M8[m]')
from uniplot import plot
plot(xs=dates, ys=[1,2,3,2])
```

Result:
```
┌────────────────────────────────────────────────────────────┐
│                                       ▝                    │ 3
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                    ▘                                      ▝│ 2
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│▖                                                           │ 1
└────────────────────────────────────────────────────────────┘
 12:24:51  12:54:54  13:24:58  13:55:01  14:25:05   14:55:09
```


## Installation

Install via pip using:

```sh
pip install uniplot
```


## Contributing

Clone this repository, and install dependecies via `poetry install`.

You can run the tests via `poetry run ./run_tests` to make sure your setup is good. Then
proceed with issues, PRs etc. the usual way.
