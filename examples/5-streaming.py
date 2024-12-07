from uniplot import plot_gen
import numpy as np
import time

MAX_SECONDS = 30

xs = np.array([np.datetime64("now")])
ys = np.array([0.0])

# Initialize plot object
plt = plot_gen(title="Streaming ...", lines=True)

for _ in range(MAX_SECONDS):
    xs = np.append(xs, [np.datetime64("now")])
    next_input_value = np.random.normal() + ys.sum() / 40.0
    ys = np.append(ys, [next_input_value])

    # Draw plot with new values
    plt.update(xs=xs, ys=ys)

    # Wait for 1s (simulating the data rate of some input stream)
    time.sleep(1)

print("Done.")
