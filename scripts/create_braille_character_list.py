import uniplot.plot_elements as elements

import numpy as np


arr = np.zeros(8)
cs = []


def increase_bitmask(x):
    shift = False
    for i in range(len(x)):
        if x[i] == 0:
            x[i] = 1
            if shift:
                x[0:i] = 0
            return
        shift = True


for i in range(256):
    c = elements.character_for_2by4_pixels(arr.reshape((4, 2)))
    cs.append(c)
    increase_bitmask(arr)

print('"' + '","'.join(cs) + '"')
