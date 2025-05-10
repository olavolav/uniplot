from uniplot import plot
from uniplot.color_themes import COLOR_THEMES

NR_LINES = 10
xs = [[i, i + NR_LINES] for i in range(NR_LINES)]
ys = [[0, 1] for _ in range(NR_LINES)]

for theme in COLOR_THEMES.keys():
    plot(
        xs=xs,
        ys=ys,
        lines=True,
        color=theme,
        title=f"Color theme: {theme}",
        x_gridlines=[],
        y_gridlines=[],
    )
    print()
