# Uniplot
[![Build Status](https://travis-ci.org/olavolav/uniplot.svg?branch=master)](https://travis-ci.org/olavolav/uniplot)
[![PyPI version](https://badge.fury.io/py/uniplot.svg)](https://pypi.org/project/uniplot/)

Simple plotting tool.

When working with production data science code it can be handy to have plotting
tool that does not rely on graphics dependencies or works only in a Jupyter notebook.

The **use case** that this was built for is to have plots as part of your data science /
machine learning CI pipeline - that way whenever something goes wrong, you get not only
the error and backtrace but also plots that show what the problem was.

Demo:
[On asciinema](https://asciinema.org/a/Ldgn5pHOgxPJmIf2ZvlfIPR3L)
[On Youtube](https://youtu.be/rZxGAGMjP5k)

[![asciicast](https://asciinema.org/a/Ldgn5pHOgxPJmIf2ZvlfIPR3L.png)](https://asciinema.org/a/Ldgn5pHOgxPJmIf2ZvlfIPR3L)


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


## Options

The `plot` function accepts the following parameters:

* `ys` - The y coordinates of the points to plot. Can either be a list or NumPy array for plotting a single series, or a list of those for plotting multiple series.
* `xs` - The x coordinates of the points to plot. Can either be `None`, or a list or NumPy array for plotting a single series, or a list of those for plotting multiple series. Defaults to `None`.
* `x_min` - Minimum x value of the view. Defaults to a value that shows all data points.
* `x_max` - Maximum x value of the view. Defaults to a value that shows all data points.
* `y_min` - Minimum y value of the view. Defaults to a value that shows all data points.
* `y_max` - Maximum y value of the view. Defaults to a value that shows all data points.
* `title` - The title of the plot. Defaults to `None`.
* `y_gridlines` - A list of y values that have a horizontal line for better orientation. Defaults to `[0]`.
* `x_gridlines` - A list of x values that have a vertical line for better orientation. Defaults to `[0]`.
* `legend_labels` - Labels for the series. Can be `None` or a list of strings. Defaults to `None`.
* `width` - The width of the plotting region, in characters. Default is `60`.
* `height` - The height of the plotting region, in characters. Default is `17`.
* `interactive` - Enable interactive mode. Defaults to `False`.
* `color` - Draw series in color. Defaults to `False` when plotting a single series, and to `True` when plotting multiple.

Note that only `ys` is a required argument, all others are optional.


## Installation

Install via pip using:

```
pip install uniplot
```


## Roadmap

Coming up:

* Line drawing
* Add flag to disable Unicode
* Add generated page with list of supported fonts
