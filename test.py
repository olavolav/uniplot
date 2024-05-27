from turtle import title

from matplotlib import interactive
from uniplot.uniplot import plot, plot_to_string


# plot([1,2,3,4,1,2,1,3,2])q

# string = plot_to_string([1,2,3,4,1,2,1,3,2], title="hola")
# plot([1,2,3,4,1,2,1,3,2], title="hola")
# st = '\n'.join(string)

# print(st)

plot([1, 2, 3, 4, 1, 2, 1, 3, 2], title="hola", interactive=True)
