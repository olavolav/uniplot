import math
from uniplot import plot

ys = [math.sin(i / 20) + i / 300 for i in range(600)]

plot(ys, title="Sine wave")
