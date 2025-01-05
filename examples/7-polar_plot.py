# Example adapted from matplotlib documentation
# Ref.: https://matplotlib.org/stable/gallery/pie_and_polar_charts/polar_demo.html

from uniplot import plot
import numpy as np

# Define spiral in polar corrdinates
r = np.arange(0, 2, 0.01)
theta = 2 * np.pi * r

# Convert to Cartesian coordinates
xs = r * np.cos(theta)
ys = r * np.sin(theta)

plot(
    xs=xs,
    ys=ys,
    lines=True,
    color=True,
    title="A line plot on a polar axis",
    x_min=-2.1,
    x_max=2.1,
    y_min=-2.1,
    y_max=2.1,
    height=20,
    width=40,
)
