from typing import Final
from uniplot.colors import ANSI_COLOR_CODES, Color

# Tableu default colors
# Ref.: https://www.tableau.com/blog/colors-upgrade-tableau-10-56782
# They are identical to the default Matplotlib colors
# Ref.: https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def
# And also to the D3 categorical10 colors
# Ref.: https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#categorical-colors
TABLEAU_COLORS: Final = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

# Default colors of Mathematica
# Ref.: https://mathematica.stackexchange.com/questions/54629/what-are-the-standard-colors-for-plots-in-mathematica-10
MATHEMATICA_COLORS: Final = [
    (101, 128, 177),
    (215, 159, 65),
    (150, 175, 72),
    (219, 107, 66),
    (132, 121, 175),
    (186, 114, 48),
    (109, 157, 195),
    (245, 193, 66),
    (156, 99, 154),
    (147, 150, 46),
    (216, 95, 65),
    (109, 132, 211),
    (235, 163, 62),
    (176, 96, 127),
    (102, 180, 116),
]

# Default colors of Plotly
# Ref.: https://plotly.com/python/discrete-color/#color-sequences-in-plotly-express
PLOTLY_COLORS: Final = [
    "#636EFA",
    "#EF553B",
    "#00CC96",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
    "#FF6692",
    "#B6E880",
    "#FF97FF",
    "#FECB52",
]

# Colors of D3 for 'category20'
# Ref.: https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#categorical-colors
D3CATEGORY20_COLORS: Final = [
    "#1f77b4",
    "#aec7e8",
    "#ff7f0e",
    "#ffbb78",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
    "#8c564b",
    "#c49c94",
    "#e377c2",
    "#f7b6d2",
    "#7f7f7f",
    "#c7c7c7",
    "#bcbd22",
    "#dbdb8d",
    "#17becf",
    "#9edae5",
]

COLOR_THEMES: Final = {
    "default": [Color.from_terminal(c) for c in list(ANSI_COLOR_CODES.keys())[0:6]],
    "tableau": [Color.from_hex(c) for c in TABLEAU_COLORS],
    "mathematica": [Color.from_rgb(*c) for c in MATHEMATICA_COLORS],
    "plotly": [Color.from_hex(c) for c in PLOTLY_COLORS],
    "d3category20": [Color.from_hex(c) for c in D3CATEGORY20_COLORS],
}
