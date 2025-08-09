from uniplot import plot
import numpy as np
from pyinstrument import profile

print("Warming up ....")
ys = np.random.random(10)
plot(ys)

ys = np.random.random(1_000_000)

with profile(interval=0.0001):
    plot(ys)

print("Done.")