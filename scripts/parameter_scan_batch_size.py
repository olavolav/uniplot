import resource
import gc
from functools import partial

import numpy as np
from time import time
from uniplot import plot
from uniplot.pixel_matrix import render

results_plot = partial(plot, character_set="ascii", color=False)


NOTICEABLE_DELAY_SECONDS = 0.2

# Set random seed for reproducibility
np.random.seed(42)

times = []
times_with_lines = []
memory = []
memory_with_lines = []

BATCH_SIZES = [10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
NR_SAMPLES = 1_000_000


def benchmark_plot(ys, lines, batch_size, num_runs=5):
    times = []
    xs = np.arange(0, len(ys), step=1)
    for _ in range(num_runs):
        start_time = time()
        render(
            xs,
            ys,
            x_min=0,
            x_max=len(xs),
            y_min=min(ys),
            y_max=max(ys),
            width=60,
            height=17,
            lines=lines,
            batch_size=batch_size,
        )
        end_time = time()
        times.append(end_time - start_time)
    return np.mean(times)


ys = np.random.uniform(size=NR_SAMPLES)

print(f"Starting benchmark with {NR_SAMPLES} samples:")
for batch_size in BATCH_SIZES:
    print(f"Benchmarking size {batch_size}...")

    # Without lines
    gc.collect()
    times.append(benchmark_plot(ys, lines=False, batch_size=batch_size))
    memory.append(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9)

    # With lines
    gc.collect()
    times_with_lines.append(benchmark_plot(ys, lines=True, batch_size=batch_size))
    memory_with_lines.append(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9)

print("Benchmarking done.")

print(f"batch_size = {BATCH_SIZES}")
print(f"times = {times}")
print(f"times_with_lines = {times_with_lines}")
print(f"memory = {memory}")
print(f"memory_with_lines = {memory_with_lines}")

results_plot(
    xs=BATCH_SIZES,
    ys=times,
    lines=True,
    title="Batch size versus plotting time, dots only, log-log",
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

results_plot(
    xs=BATCH_SIZES,
    ys=memory,
    lines=True,
    title="Batch size versus memory use, dots only, log-log",
    y_unit=" GB",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

results_plot(
    xs=BATCH_SIZES,
    ys=times_with_lines,
    lines=True,
    title="Batch size versus plotting time, dots + lines, log-log",
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

results_plot(
    xs=BATCH_SIZES,
    ys=memory_with_lines,
    lines=True,
    title="Batch size versus memory use, dots + lines, log-log",
    y_unit=" GB",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

# Combined plot
results_plot(
    xs=[BATCH_SIZES] * 2,
    ys=[times, times_with_lines],
    lines=True,
    title="Batch size versus plotting time",
    legend_labels=["dots only", "dots + lines"],
    y_unit=" s",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

results_plot(
    xs=[BATCH_SIZES] * 2,
    ys=[memory, memory_with_lines],
    lines=True,
    title="Batch size versus memory use",
    legend_labels=["dots only", "dots + lines"],
    y_unit=" GB",
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[NOTICEABLE_DELAY_SECONDS],
)

# Mem-runtime combination
results_plot(
    xs=[BATCH_SIZES] * 2,
    ys=[times, memory],
    lines=True,
    title="Batch size versus performance, dots only",
    legend_labels=["runtime [s]", "peak memory [GB]"],
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[],
)

results_plot(
    xs=[BATCH_SIZES] * 2,
    ys=[times_with_lines, memory_with_lines],
    lines=True,
    title="Batch size versus performance, dots+lines",
    legend_labels=["runtime [s]", "peak memory [GB]"],
    x_as_log=True,
    y_as_log=True,
    y_gridlines=[],
)
