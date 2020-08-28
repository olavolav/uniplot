# Uniplot

Simple plotting tool.

When working with production data science code it can be handy to have simple plotting
tool that does not rely on graphics dependencies or works only in a Jupyter notebook.

I use this all the time when transforming exploratory code to production Python code.
Another use case is having plots as part of your validation tests - that way when
something goes wrong, you get not only the error and backtrace but also plots that show
you what the problem was.


## Features

* Unicode drawing, so 4x the resolution (pixels) of usual ASCII plots
* Super simple API
* Interactive mode (simply pass `interactive=True`) see [the (slightly outdated) demo video](https://www.youtube.com/watch?v=nmYeBL_0K4A)
* It's fast: Plotting 1M data points takes 100ms thanks to NumPy magic
* Only one dependency: NumPy (but you have that anyway don't you)

Please note that Unicode drawing will work correctly only when using a font that
fully supports the [Box-drawing character set](https://en.wikipedia.org/wiki/Box-drawing_character).
Please refer to [this page for a (incomplete) list of supported fonts](https://www.fileformat.info/info/unicode/block/block_elements/fontsupport.htm).


## Examples

```
>>> import math
>>> x = [math.sin(i/20)+i/300 for i in range(600)]
>>> from uniplot import plot
>>> plot(x, title="Sine wave")
                          Sine wave
┌────────────────────────────────────────────────────────────┐
│                                                   ▗▛▜▖     │ 2.7
│                                                   ▟  ▜     │
│                                       ▐▀▙        ▗▌  ▝▌    │
│                                      ▗▌ ▝▌       ▟    ▜    │
│                           ▞▜▖        ▟   ▜       ▌    ▝▌   │ 1.9
│                          ▟  ▜        ▌   ▝▌     ▐      ▚   │
│              ▗▛▙        ▗▌  ▝▌      ▐     ▜     ▛      ▝▖  │
│              ▛ ▝▌       ▐    ▜      ▛     ▝▌   ▗▘       ▚  │
│  ▟▜▖        ▐   ▐       ▌    ▝▌    ▗▘      ▚   ▟        ▝▙▖│ 1.1
│ ▐▘ ▜        ▌    ▌     ▐▘     ▜    ▟       ▝▌ ▗▌           │
│ ▌   ▌      ▐▘    ▜     ▞      ▝▖   ▌        ▜▄▞            │
│▐    ▐      ▞     ▝▌    ▌       ▜  ▟                        │
│▛    ▝▌     ▌      ▜   ▐        ▝▙▄▘                        │ 0.2
│▌─────▜────▐───────▝▌──▛────────────────────────────────────│
│      ▝▌   ▛        ▜▄▟                                     │
│       ▜  ▐▘                                                │
│       ▝▙▄▌                                                 │ -0.6
└────────────────────────────────────────────────────────────┘
 1.0                                                      606.0
```


## Options

The `plot` function accepts the following parameters:

* `ys` - A list or NumPy array of numerical values of the y coordinates of the points to plot.
* `xs` - A list or NumPy array of numerical values of the x coordinates of the points to plot.
* `x_min` - Minimum x value of the view. Defaults to a value that shows all data points.
* `x_max` - Maximum x value of the view. Defaults to a value that shows all data points.
* `y_min` - Minimum y value of the view. Defaults to a value that shows all data points.
* `y_max` - Maximum y value of the view. Defaults to a value that shows all data points.
* `title` - The title of the plot. Defaults to `None`.
* `y_gridlines` - A list of y values that have a horizontal line for better orientation. Defaults to `[0]`
* `x_gridlines` - A list of x values that have a vertical line for better orientation. Defaults to `[0]`
* `width` - The width of the plotting region, in characters. Default is `60`.
* `height` - The height of the plotting region, in characters. Default is `17`.
* `interactive` - Enable interactive mode. Defaults to `False`.

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
