import numpy as np
import pandas as pd

from uniplot import plot


uri = "https://github.com/owid/owid-datasets/raw/master/datasets/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre.csv"
data = pd.read_csv(uri)
data = data.rename(
    columns={"Global average temperature anomaly (Hadley Centre)": "Global"}
)
data = data[data.Entity == "median"]

# First plot using years as number
plot(
    xs=data.Year,
    ys=data.Global,
    lines=True,
    title="Global normalized land-sea temperature anomaly",
    y_unit=" °C",
)

# now with year as datetime
data["Date"] = np.array(data.Year - 1970, dtype="datetime64[Y]")
plot(
    xs=data.Date,
    ys=data.Global,
    lines=True,
    title="Global normalized land-sea temperature anomaly",
    y_unit=" °C",
)
