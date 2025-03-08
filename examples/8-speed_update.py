from uniplot import plot_gen
from collections import deque
import time
import math


def wave_generator(a1=1, frequency=1, phase_shift=0.4, f2=6.1343):
    t = 0
    while t < 100:  # Infinite generator
        value = (
            a1 * math.sin(frequency * t + phase_shift)
            + 0.5 * math.cos(f2 * t)
            + 2.5 * math.cos(0.71 * t)
        )
        yield value  # Yield the wave value with optional offset
        t += 0.1  # Increment t (time) to move along the wave


max_len = 200

deq = deque([0] * max_len, maxlen=max_len)

plt = plot_gen(width=100, y_unit="$", title="Price", color=["green"], y_min=-5, y_max=5)

start = time.perf_counter()
for i in wave_generator():
    deq.append(i)
    deq2 = [0.8 + i * 0.3 for i in deq]
    plt.update(ys=[deq])
stop = time.perf_counter()

print(f"Time: {stop - start}s")
