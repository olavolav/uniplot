"""Show random service metrics as sparklines and a larger filled chart."""

import numpy as np

from uniplot import plot, sparkline_to_string

# Interpolate random samples into one reading per minute for an hour.
rng = np.random.default_rng()
minutes = np.arange(60)
samples = np.linspace(0, 59, 10)
requests = np.interp(minutes, samples, rng.uniform(100, 1000, 10))
latency = np.interp(minutes, samples, rng.uniform(10, 100, 10))
errors = np.interp(minutes, samples, rng.uniform(0, 2, 10))

print("Service activity — last hour\n")
for label, values, color, maximum in [
    ("Requests/min", requests, "cyan", 1000),
    ("Latency (ms)", latency, "magenta", 100),
    ("Errors (%)", errors, "yellow", 2),
]:
    chart = sparkline_to_string(values, width=24, color=[color], y_min=0, y_max=maximum)
    print(f"{label:<14} {chart} {values[-1]:6.1f}")

print()
plot(
    requests,
    fill=0,
    lines=True,
    color=["cyan"],
    title="Requests per minute",
    width=60,
    height=10,
    y_min=0,
    y_max=1000,
    x_unit=" min",
    x_gridlines=[],
    y_gridlines=[],
)
