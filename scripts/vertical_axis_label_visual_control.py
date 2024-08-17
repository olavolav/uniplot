from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels


x_min = 6.5
x_max = 7.5
for _ in range(150):
    x_max = x_max * 1.05
    space = 17

    ls = extended_talbot_labels(
        x_min=x_min, x_max=x_max, available_space=space, vertical_direction=True
    )
    if ls is None:
        raise
    strings = ls.render()

    print("┐")
    for s in strings:
        print("| " + s)
    print("┘")
    print()
