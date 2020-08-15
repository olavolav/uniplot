# Textplot

Simple plotting tool.

When working with production data science code it can be handy to have simple plotting
tool that does not rely on graphics dependencies or works only in a Jupyter notebook.

I use this all the time when transforming exploratory code to production Python code.
Another use case is having plots as part of your validation tests - that way when
something goes wrong, you get not only the error and backtrace but also plots that show
you what the problem was.

## Examples

```
>>> import math
>>> import textplot.plot as plot
>>> x = [math.sin(i/20)+i/300 for i in range(600)]
>>> plot.plot(x, title="Sine wave")
                          Sine wave
┌────────────────────────────────────────────────────────────┐
│                                                    ▟▀▚     │ 2.8843220477363056
│                                                   ▗▘ ▝▌    │
│                                       ▗▛▜▖        ▞   ▐    │
│                                       ▞  ▜       ▗▌    ▌   │
│                           ▟▀▙        ▗▘  ▝▌      ▐     ▜   │ 2.067778850823121
│                          ▐▘ ▝▖       ▞    ▜      ▌     ▝▌  │
│              ▗▛▜▖        ▛   ▜      ▗▌    ▝▌    ▐▘      ▜  │
│              ▛  ▙       ▗▘   ▝▖     ▐      ▚    ▞       ▝▌ │
│  ▟▀▖        ▐▘  ▝▖      ▟     ▚     ▌      ▝▖  ▗▌        ▜▄│ 1.2512356539099354
│ ▐▘ ▐▖       ▛    ▙      ▌     ▐▖   ▗▘       ▚  ▞           │
│ ▛   ▙      ▗▘    ▐▖    ▐       ▙   ▞        ▝▙▟▘           │
│▐▘   ▐▖     ▐      ▌    ▛       ▐▖ ▗▘                       │
│▞     ▌     ▌      ▐   ▗▘        ▜▄▛                        │ 0.4346924569967503
│▌     ▐    ▐▘       ▙  ▞                                    │
│       ▌   ▛        ▝▄▟▘                                    │
│       ▜  ▐▘                                                │
│        ▙▄▛                                                 │ -0.3818507399164349
└────────────────────────────────────────────────────────────┘
1 up to 600```

## Roadmap

Coming up:

* Line drawing
* Add flag to disable Unicode
* Interactive mode
