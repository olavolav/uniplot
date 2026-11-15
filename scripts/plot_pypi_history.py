import pandas as pd

from uniplot import plot

CSV_FILE = "uniplot_download_history.csv"

data = pd.read_csv(CSV_FILE)

plot(
    xs=data["date"],
    ys=data["cumulative_downloads"],
    lines=True,
    fill=[0],
    color=True,
    x_gridlines=[],
    y_gridlines=[],
)
plot(
    xs=data["date"],
    ys=data["cumulative_downloads"],
    lines=True,
    fill=["bottom"],
    color=True,
    x_gridlines=[],
    y_gridlines=[],
    y_as_log=True,
    y_unit_scaling="si",
)
