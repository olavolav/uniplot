import random
import time
import datetime

from uniplot import plot_gen

MAX_SECONDS = 30

# Initialize lists for values of x and y coordinates
xs = []
ys = []

# Initialize plot object with default options
plt = plot_gen(width=100, lines=True, color=True)

for _ in range(MAX_SECONDS):
    # Append current time stamp
    xs.append(datetime.datetime.now())
    # Append a random number (normal distribution)
    ys.append(random.gauss(0.5, 1.0))

    # Draw plot with new values
    plt.update(xs=xs, ys=ys, title=f"Streaming: {len(ys)} data point(s) ...")

    # Wait for 1s (simulating the data rate of some input stream)
    time.sleep(1)

print("Done.")
