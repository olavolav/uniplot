from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels

NR_RUNS: int = 150

x_min = 6.5
x_max = 7.5
nr_runs_with_blank_labels: int = 0
for i in range(NR_RUNS):
    x_max = x_max * 1.05
    space = 60

    ls = extended_talbot_labels(
        x_min=x_min, x_max=x_max, available_space=space, vertical_direction=False
    )
    str_labels = ls.render()[0]
    print(str_labels)

    if str_labels.strip() == "":
        print(f"Found an empty label set for x_min = {x_min} and x_max = {x_max}")
        nr_runs_with_blank_labels += 1

print(f"\nIn total, found {nr_runs_with_blank_labels} case(s) with blank labels.")
