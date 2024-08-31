from uniplot import plot_to_string
import time
import curses
import numpy as np

ys = np.sin(np.linspace(1,200))

def main(screen):
    screen.clear()
    plt = plot_to_string(ys, title="Sine waves", legend_labels=["Original", "Shifted and scaled waves"], color=False)
    [screen.addstr(i, 0, line) for (i, line) in enumerate(plt)]
    screen.refresh()
    time.sleep(3)

curses.wrapper(main)
