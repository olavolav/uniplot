import numpy as np
from uniplot import plot

dates = np.arange("2002-10-27T04:30", 4 * 60, 60, dtype="M8[m]")

plot(xs=dates, ys=[1, 2, 3, 2], title="Plotting time series")
