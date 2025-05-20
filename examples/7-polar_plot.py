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

print()
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
    height=30,
    width=60,
)

# Ref.: https://www.matematica.pt/en/useful/list-curves.php
a = 5.0
b = 7.0
c = 3
t = np.arange(0, 200, 0.01)
xs = (a - b) * np.cos(t) + c * np.cos((a / b - 1) * t)
ys = (a - b) * np.sin(t) + c * np.sin((a / b - 1) * t)
print()
plot(xs=xs, ys=ys, lines=True, color=True, title="A hypotrochoid", height=30, width=60)
