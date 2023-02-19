import numpy as np
from time import time
from uniplot import plot

NOTICEABLE_DELAY_SECONDS = 0.2

sizes = []
times = []
times_with_lines = []

# Historical data
historical_version = "v0.9.1"
historical_sizes = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]
historical_times = [
    0.014598846435546875,
    0.016776084899902344,
    0.010040044784545898,
    0.010375261306762695,
    0.0107879638671875,
    0.018589019775390625,
    0.06313228607177734,
    0.6484909057617188,
]
historical_times_with_lines = [
    0.02862381935119629,
    0.010422945022583008,
    0.01305389404296875,
    0.01655888557434082,
    0.05128192901611328,
    0.3673999309539795,
    3.5426928997039795,
    36.34388995170593,
]

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
    xs=[historical_sizes, sizes],
    ys=[historical_times, times],
    lines=True,
    title="Sample size versus plotting time, dots only, log-log",
    legend_labels=[historical_version, "current"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

plot(
    xs=[historical_sizes, sizes],
    ys=[historical_times_with_lines, times_with_lines],
    lines=True,
    title="Sample size versus plotting time, dots + lines, log-log",
    legend_labels=[historical_version, "current"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

# Combined plot
plot(
    xs=[sizes, sizes],
    ys=[times, times_with_lines],
    lines=True,
    title="Sample size versus plotting time, log-log, current cersion",
    legend_labels=["dots only", "dots + lines"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)
