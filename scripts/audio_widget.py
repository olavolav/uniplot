import argparse
from wave import open as open_wave
import numpy as np

from uniplot import plot_gen
from uniplot.getch import getch

MAX_FRAMES = 100_000
MONO_DISPLAY_OFFSET = 20_000

parser = argparse.ArgumentParser(prog="Uniplot Audio Widget")

parser.add_argument("filename")
args = parser.parse_args()


def read_from_wave_file(file_name: str):
    wave_file = open_wave(file_name, "rb")
    nr_frames = wave_file.getnframes()
    nr_channels = wave_file.getnchannels()
    print(f"File contains {nr_frames} frame(s) and {nr_channels} channel(s).")
    wav_frames = wave_file.readframes(min(nr_frames, MAX_FRAMES))
    return np.fromstring(wav_frames, dtype=np.int16)


ys = read_from_wave_file(args.filename)

x_gridlines = [0]
plt = plot_gen(
    title=args.filename,
    width=100,
    x_gridlines=[],
    y_gridlines=[],
    color=["red", "blue"],
    y_labels=False,
)
while True:
    x_gridlines_color = ["red"] * (len(x_gridlines) - 1) + [False]
    plt.update(
        ys=[ys, ys + MONO_DISPLAY_OFFSET],
        x_gridlines=x_gridlines,
        x_gridlines_color=x_gridlines_color,
    )
    key_pressed = getch().lower()
    if key_pressed == "h":
        x_gridlines[-1] -= 5_000
    elif key_pressed == "l":
        x_gridlines[-1] += 5_000
    elif key_pressed == "m":
        x_gridlines.append(x_gridlines[-1])
    elif key_pressed in ["q", "\x1b"]:
        break
