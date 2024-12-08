import math
from uniplot import plot

# Set up y axis valus based on two different shifted sine waves
ys = [
    [math.sin(i / (10 + i / 50)) - math.sin(i / 100) for i in range(1000)],
    [math.sin(i / (10 + i / 50)) - math.sin(i / 100) - 1 for i in range(900)],
]

# Plotting
plot(ys, lines=True, x_unit="s", title="Double sine wave")
