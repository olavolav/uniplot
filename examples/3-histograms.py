import math
from uniplot import histogram

ys = [
    [math.sin(i / (10 + i / 50)) - math.sin(i / 100) for i in range(1000)],
    [math.sin(i / (10 + i / 50)) - math.sin(i / 100) - 1 for i in range(900)],
]

histogram(
    ys, title="Histograms of the above", legend_labels=["wave", "wave with offset of 1"]
)
