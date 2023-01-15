import numpy as np
from time import time
from uniplot import plot

expo: int = 0
expos = []
sizes = []
times = []
times_with_lines = []

for expo in range(9):
    expos.append(expo)
    size = 10**expo
    sizes.append(size)
    ys = np.random.uniform(size=size)

    # Without lines
    start_time = time()
    plot(ys, title=f"Plotting 10^{expo} random samples", lines=False)
    end_time = time()
    times.append(end_time - start_time)

    # With lines
    start_time = time()
    plot(ys, title=f"Plotting 10^{expo} random samples with lines", lines=True)
    end_time = time()
    times_with_lines.append(end_time - start_time)


print("Benchmarking done.")

print(f"expos = {expos}")
print(f"sizes = {sizes}")
print(f"times = {times}")
print(f"times_with_lines = {times_with_lines}")

plot(xs=sizes, ys=times, lines=True, title="sizes versus plotting time", y_unit=" s")
plot(
    xs=sizes,
    ys=times_with_lines,
    lines=True,
    title="sizes versus plotting time, with lines",
    y_unit=" s",
)
plot(xs=expos, ys=times, lines=True, title="expos versus plotting time", y_unit=" s")
plot(
    xs=expos,
    ys=times_with_lines,
    lines=True,
    title="expos versus plotting time, with lines",
    y_unit=" s",
)
plot(xs=expos, ys=np.log(times), lines=True, title="expos versus log plotting time")
plot(
    xs=expos,
    ys=np.log(times_with_lines),
    lines=True,
    title="expos versus log plotting time, with lines",
)
