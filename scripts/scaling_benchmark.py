import numpy as np
from time import time
from uniplot import plot

sizes = []
times = []
times_with_lines = []

for expo in range(8):
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

print(f"sizes = {sizes}")
print(f"times = {times}")
print(f"times_with_lines = {times_with_lines}")

plot(
    xs=sizes,
    ys=times,
    lines=True,
    title="Sample size versus plotting time, without lines, log-log",
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
)

plot(
    xs=sizes,
    ys=times_with_lines,
    lines=True,
    title="Sample size versus plotting time, with lines, log-log",
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
)
