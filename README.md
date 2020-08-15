# Textplot

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
* Interactive mode (simply pass `interactive=True`) see [demo video](https://www.youtube.com/watch?v=nmYeBL_0K4A)
* It's fast: Plotting 1M data points takes 100ms thanks to NumPy magic
* Only one dependency: NumPy (but you have that anyway don't you)

## Examples

```
>>> import math
>>> import textplot.plot as plot
>>> x = [math.sin(i/20)+i/300 for i in range(600)]
>>> plot.plot(x, title="Sine wave")
                          Sine wave
┌────────────────────────────────────────────────────────────┐
│                                                    ▟▀▚     │ 2.9
│                                                   ▗▘ ▝▌    │
│                                       ▗▛▜▖        ▞   ▐    │
│                                       ▞  ▜       ▗▌    ▌   │
│                           ▟▀▙        ▗▘  ▝▌      ▐     ▜   │ 2.1
│                          ▐▘ ▝▖       ▞    ▜      ▌     ▝▌  │
│              ▗▛▜▖        ▛   ▜      ▗▌    ▝▌    ▐▘      ▜  │
│              ▛  ▙       ▗▘   ▝▖     ▐      ▚    ▞       ▝▌ │
│  ▟▀▖        ▐▘  ▝▖      ▟     ▚     ▌      ▝▖  ▗▌        ▜▄│ 1.3
│ ▐▘ ▐▖       ▛    ▙      ▌     ▐▖   ▗▘       ▚  ▞           │
│ ▛   ▙      ▗▘    ▐▖    ▐       ▙   ▞        ▝▙▟▘           │
│▐▘   ▐▖     ▐      ▌    ▛       ▐▖ ▗▘                       │
│▞     ▌     ▌      ▐   ▗▘        ▜▄▛                        │ 0.4
│▌     ▐    ▐▘       ▙  ▞                                    │
│       ▌   ▛        ▝▄▟▘                                    │
│       ▜  ▐▘                                                │
│        ▙▄▛                                                 │ -0.4
└────────────────────────────────────────────────────────────┘
1.0                                                      600.0
```

## Roadmap

Coming up:

* Line drawing
* Add flag to disable Unicode
