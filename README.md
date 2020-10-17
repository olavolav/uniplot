# Uniplot
[![Build Status](https://travis-ci.org/olavolav/uniplot.svg?branch=master)](https://travis-ci.org/olavolav/uniplot)
[![PyPI Version](https://badge.fury.io/py/uniplot.svg)](https://pypi.org/project/uniplot/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/uniplot)](https://pypistats.org/packages/uniplot)

Lightweight plotting to the terminal. 4x resolution via Unicode.

[![uniplot demo GIF](https://github.com/olavolav/uniplot/raw/master/resource/uniplot-demo.gif)](https://asciinema.org/a/Ldgn5pHOgxPJmIf2ZvlfIPR3L)

When working with production data science code it can be handy to have plotting
tool that does not rely on graphics dependencies or works only in a Jupyter notebook.

The **use case** that this was built for is to have plots as part of your data science /
machine learning CI pipeline - that way whenever something goes wrong, you get not only
the error and backtrace but also plots that show what the problem was.


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


## Example

```
>>> import math
>>> x = [math.sin(i/20)+i/300 for i in range(600)]
>>> from uniplot import plot
>>> plot(x, title="Sine wave")
                          Sine wave
┌────────────────────────────────────────────────────────────┐
│                                                    ▟▀▚     │ 2.7
│                                                   ▗▘ ▝▌    │
│                                       ▗▛▜▖        ▞   ▐    │
│                                       ▞  ▜       ▗▌    ▌   │
│                           ▟▀▙        ▗▘  ▝▌      ▐     ▜   │ 1.9
│                          ▐▘ ▝▖       ▞    ▜      ▌     ▝▌  │
│              ▗▛▜▖        ▛   ▜      ▗▌    ▝▌    ▐▘      ▜  │
│              ▛  ▙       ▗▘   ▝▖     ▐      ▚    ▞       ▝▌ │
│  ▟▀▖        ▐▘  ▝▖      ▟     ▚     ▌      ▝▖  ▗▌        ▜▄│ 1.0
│ ▐▘ ▐▖       ▛    ▙      ▌     ▐▖   ▗▘       ▚  ▞           │
│ ▛   ▙      ▗▘    ▐▖    ▐       ▙   ▞        ▝▙▟▘           │
│▐▘   ▐▖     ▐      ▌    ▛       ▐▖ ▗▘                       │
│▞     ▌     ▌      ▐   ▗▘        ▜▄▛                        │ 0.2
│▌─────▐────▐▘───────▙──▞────────────────────────────────────│
│       ▌   ▛        ▝▄▟▘                                    │
│       ▜  ▐▘                                                │
│        ▙▄▛                                                 │ -0.6
└────────────────────────────────────────────────────────────┘
 1                                                        600
```


## Parameters

The `plot` function accepts a number of parameters, all listed below. Note that only
`ys` is required, all others are optional.


### Data

* `xs` - The x coordinates of the points to plot. Can either be `None`, or a list or NumPy array for plotting a single series, or a list of those for plotting multiple series. Defaults to `None`, meaning that the x axis will be just the sample index of
`ys`.
* `ys` - The y coordinates of the points to plot. Can either be a list or NumPy array for plotting a single series, or a list of those for plotting multiple series.

### Options

In alphabetical order:

* `color` - Draw series in color. Defaults to `False` when plotting a single series, and to `True` when plotting multiple.
* `height` - The height of the plotting region, in characters. Default is `17`.
* `interactive` - Enable interactive mode. Defaults to `False`.
* `legend_labels` - Labels for the series. Can be `None` or a list of strings. Defaults to `None`.
* `lines` - Draw lines between points. Defaults to `False`.
* `title` - The title of the plot. Defaults to `None`.
* `width` - The width of the plotting region, in characters. Default is `60`.
* `x_gridlines` - A list of x values that have a vertical line for better orientation. Defaults to `[0]`.
* `x_max` - Maximum x value of the view. Defaults to a value that shows all data points.
* `x_min` - Minimum x value of the view. Defaults to a value that shows all data points.
* `y_gridlines` - A list of y values that have a horizontal line for better orientation. Defaults to `[0]`.
* `y_max` - Maximum y value of the view. Defaults to a value that shows all data points.
* `y_min` - Minimum y value of the view. Defaults to a value that shows all data points.


## Experimental features

For convenience there is also a `histogram` function that accepts one or more series and
plots bar-chart like histograms. It will automatically discretize the series into a
number of bins given by the `bins` option and display the result.

When calling the `histogram` function, the `lines` option is `True` by default.


## Installation

Install via pip using:

```
pip install uniplot
```


## Roadmap

Coming up:

* Fill area under curve
* Add generated page with list of supported fonts
