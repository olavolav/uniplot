import numpy as np
from uniplot import plot

# Set up x and y coordinates, where x coordinates are NumPy datetime64 time stamps
dates = np.arange("2002-10-27T04:30", 4 * 60, 60, dtype="M8[m]")
ys = [1, 2, 3, 2]

# Plotting
plot(xs=dates, ys=ys, title="Plotting time series")
