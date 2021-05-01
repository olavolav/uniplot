from uniplot.axis_labels.extended_talbot_labels import extended_talbot_labels


x_min = 6.5
x_max = 7.5
for i in range(150):
    x_max = x_max * 1.05
    space = 60

    ls = extended_talbot_labels(x_min=x_min, x_max=x_max, available_space=space, vertical_direction=False)
    print(ls.render()[0])
