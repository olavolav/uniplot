import math
from uniplot import plot

# Set up y axis valus based on a shifted sine wave
ys = [math.sin(i / 20) + i / 300 for i in range(600)]

# Plotting
plot(ys, title="Sine wave")
