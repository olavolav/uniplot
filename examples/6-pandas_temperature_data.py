### Plot global temperature data

# Here we are using Pandas to load and prepare global temperature data from the
# [Our World in Data GitHub repository](https://github.com/owid/owid-datasets).

import pandas as pd
from uniplot import plot

# First we load the data, rename a column and and filter the data:
print("Loading data ...")
uri = "https://github.com/owid/owid-datasets/raw/master/datasets/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre.csv"
data = pd.read_csv(uri)
# Sinplify column names
data = data.rename(
    columns={"Global average temperature anomaly (Hadley Centre)": "Global"}
)
# Create dattime column (this is optional)
data["Date"] = pd.to_datetime(data.Year, format="%Y")

print(data.head())
print(f"Done loading dataframe of shape {data.shape}.\n")

# Filter data, we only need the median values here
data = data[data.Entity == "median"]

# Then we can plot it:
plot(
    xs=data.Date,
    ys=data.Global,
    lines=True,
    title="Global normalized land-sea temperature anomaly",
    y_unit=" °C",
)
