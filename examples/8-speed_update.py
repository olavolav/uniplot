from uniplot import plot_gen
from collections import deque
import time
import math


kwargs = {
    "width": 190,
    "height": 16,
    "y_unit": "$",
    "color": ["green", "red", "blue"],
    "title": "Price",
}


def wave_generator(a1=1, frequency=1, phase_shift=0.4, f2=6.1343):
    t = 0  # Start at t=0
    while t<100:  # Infinite generator
        value = a1 * math.sin(frequency * t + phase_shift) + 0.5*math.cos(f2 * t) + 2.5*math.cos(0.71 * t)
        yield value  # Yield the wave value with optional offset
        t += 0.1  # Increment t (time) to move along the wave

max_len = 200

deq = deque([0] * max_len , maxlen=max_len)
plt = plot_gen(**kwargs)

start = time.perf_counter()
for i in wave_generator():
    deq.append(i)
    deq2 = [0.8+i*0.3 for i in deq]
    #plt.update(ys=[deq,deq2], title="test") # current error in title
    plt.update(ys=[deq], title="test") # current error in title
stop = time.perf_counter()
print(f"Time: {stop-start}s")
