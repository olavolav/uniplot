import timeit
import random

from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels

NR_RUNS = 500

def single_run():
    x_min = -5*random.random() + 1
    x_max = 1_000*random.random() + 1.5
    space = random.randint(5, 200)
    is_vertical = int(random.random() < 0.5)

    extended_talbot_labels(x_min=x_min, x_max=x_max, available_space=space, vertical_direction=is_vertical)


print("Measuring ...")
t = timeit.timeit(single_run, number=NR_RUNS) / NR_RUNS

print(f"Avg. time for single run: {1_000*t}ms (across {NR_RUNS} runs)")
