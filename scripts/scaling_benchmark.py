from functools import partial

import numpy as np
from time import time
from uniplot import plot

results_plot = partial(plot, character_set="ascii", color=False)


NOTICEABLE_DELAY_SECONDS = 0.2

# Set random seed for reproducibility
np.random.seed(42)

# Warm-up phase
plot(np.random.uniform(size=10), lines=False)
plot(np.random.uniform(size=10), lines=True)

sizes = []
times = []
times_with_lines = []

# Historical data
historical_version = "v0.9.1"
historical_sizes = [1, 10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
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


def benchmark_plot(ys, lines, num_runs=5):
    times = []
    for _ in range(num_runs):
        start_time = time()
        plot(ys, lines=lines)
        end_time = time()
        times.append(end_time - start_time)
    return np.mean(times)


for expo in range(8):
    size = 10**expo
    sizes.append(size)
    ys = np.random.uniform(size=size)

    print(f"Benchmarking size {size}...")

    # Without lines
    times.append(benchmark_plot(ys, lines=False))

    # With lines
    times_with_lines.append(benchmark_plot(ys, lines=True))

print("Benchmarking done.")

print(f"sizes = {sizes}")
print(f"times = {times}")
print(f"times_with_lines = {times_with_lines}")

results_plot(
    xs=[historical_sizes, sizes],
    ys=[historical_times, times],
    lines=True,
    title="Sample size versus plotting time, dots only, log-log",
    legend_labels=[historical_version, "current"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
    character_set="ascii",
    color=False,
)

results_plot(
    xs=[historical_sizes, sizes],
    ys=[historical_times_with_lines, times_with_lines],
    lines=True,
    title="Sample size versus plotting time, dots + lines, log-log",
    legend_labels=[historical_version, "current"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
    character_set="ascii",
    color=False,
)

# Combined plot
results_plot(
    xs=[sizes, sizes],
    ys=[times, times_with_lines],
    lines=True,
    title="Sample size versus plotting time, log-log, current version",
    legend_labels=["dots only", "dots + lines"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
    character_set="ascii",
    color=False,
)
