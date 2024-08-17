import numpy as np
from uniplot.axis_labels.datetime_labels import datetime_labels

NR_RUNS: int = 250

x_min = 6.5
x_min_as_dt = np.float64(x_min).astype("datetime64[s]")
x_max = 7.5
space = 60
nr_runs_with_blank_labels: int = 0
for i in range(NR_RUNS):
    x_max = x_max * 1.075
    x_max_as_dt = np.float64(x_max).astype("datetime64[s]")

    ls = datetime_labels(
        x_min=x_min, x_max=x_max, available_space=space, vertical_direction=False
    )
    if ls is None:
        print(
            f"Found an empty label set for x_min = {x_min_as_dt} and x_max = {x_max_as_dt}"
        )
        nr_runs_with_blank_labels += 1
        continue

    str_labels = ls.render()[0]
    print(str_labels)

    if str_labels.strip() == "":
        print(
            f"Found an empty label set for x_min = {x_min_as_dt} and x_max = {x_max_as_dt}"
        )
        nr_runs_with_blank_labels += 1

percentage = 100.0 * nr_runs_with_blank_labels / NR_RUNS
print(
    f"\n-> In total, found {nr_runs_with_blank_labels} ({int(percentage)}%) case(s) with blank labels."
)
