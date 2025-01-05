### Plot global temperature data

# Here we are using Pandas to load and prepare global temperature data from the
# [Our World in Data GitHub repository](https://github.com/owid/owid-datasets).

import pandas as pd
from uniplot import plot

INPUT_CSV_URI = "https://github.com/owid/owid-datasets/raw/master/datasets/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre.csv"

print("Loading data ...")
raw_data = pd.read_csv(INPUT_CSV_URI)
# Sinplify column names
raw_data = raw_data.rename(
    columns={"Global average temperature anomaly (Hadley Centre)": "Anomaly"}
)
print(f"Done loading dataframe of shape {raw_data.shape}.\n")

print("Transform data ...")
data = pd.DataFrame.from_records(
    [
        {
            # "Year": y,
            "Lower": g[g.Entity == "lower"]["Anomaly"].mean(),
            "Median": g[g.Entity == "median"]["Anomaly"].mean(),
            "Upper": g[g.Entity == "upper"]["Anomaly"].mean(),
            "Date": pd.to_datetime(y, format="%Y"),
        }
        for (y, g) in raw_data.groupby(raw_data.Year)
    ]
)
print(f"Done transforming dataframe to shape {data.shape}.\n")

# Then we can plot it, and for extra resolution we plot it using Braille characters
plot(
    xs=[data.Date, data.Date],
    ys=[data.Upper - data.Lower, data.Median],
    lines=True,
    title="Global normalized land-sea temperature anomaly",
    y_unit=" °C",
    legend_labels=["Temperature anomaly", "Annual variation"],
    character_set="braille",
)
