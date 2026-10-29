# Changelog

All notable changes to uniplot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.24.0] - 2026-10-29
### Added
- Unit scaling for axis labels via the new `x_unit_scaling` / `y_unit_scaling`
  options, assuming `x_unit` / `y_unit` is the base unit. Currently supports
  `"si"` (SI prefixes; more modes may follow). When set to `"si"`, labels are
  rendered with the appropriate SI prefix (e.g. a label of `1000` with unit
  `" m"` becomes `1 km`, `0.003` becomes `3 mm`). The prefix is inserted before
  the first non-whitespace character of
  the unit, so a leading space is preserved; a blank unit still gets a prefix
  (e.g. `200k`). On linear axes a single prefix is chosen for the whole axis,
  anchored to the smallest nonzero label so that no label drops below 1 in the
  chosen unit (e.g. `[250, 500, 1000]` stays in grams rather than tipping into
  fractional kilograms). A prefix is only applied when it does not make the
  labels longer than the plain representation, so e.g. `0.5 °C` is kept as-is
  rather than rewritten as `500 m°C`. On log axes each label gets its own
  prefix, since the labels span several orders of magnitude. Values beyond the
  known prefix range (below yocto or above yotta) fall back to plain
  formatting.
### Changed
- Log-scale axis labels now render the actual values (e.g. `1.6`, `100`)
  instead of exponent notation (`10^0.2`, `10^2`), which also fixes fractional
  exponents previously shown as e.g. `10^-0.6`.
- Upgraded ruff to v0.16. Numerous linter and formatting fixes.
### Fixed
- Time of datetime labels was blank when plotting with time of midnight. Thanks
  to @Flix6x for spotting and fixing this!

## [0.23.2] - 2026-07-12
### Fixed
- Timestamps for histogram x-axis are correctly displayed. Thanks @rossburton
  for reporting!

## [0.23.1] - 2026-06-23
### Fixed
- Thread-safety: `plot_gen.set_data()` now snapshots the supplied data
  (`xs`/`ys`) *and* any mutable option values (e.g. `lines`, `color`,
  `legend_labels`, gridlines) at call time, so it is safe to pass live,
  still-growing lists while `rich.live.Live` renders on its own thread.
  Previously the producer's later appends could desync a list from the series
  count and crash the background render thread (a length assertion for data, a
  `ValueError` for options). The snapshot is cheap (≈0.15 ms for a 1M-point
  NumPy array). Pass `set_data(..., copy=False)` to skip it when you already
  hand over fresh, private objects each call.

## [0.23.0] - 2026-06-21
### Added
- Integration with [Rich](https://github.com/Textualize/rich), including support
  for live-updating displays via `rich.live.Live`. A `plot_gen` object is a Rich
  renderable and exposes a thread-safe `plot_gen.set_data(...)` for feeding new
  data without printing. Install with `pip install uniplot[rich]`.
- `plot_gen.to_string()` returns the current plot as a string without printing,
  and `plot_gen.reset_view()` resets the view window and clears pinned bounds.
### Changed
- **Breaking:** `plot_gen` was simplified. `update()` now always re-draws from
  the current state and returns the rendered string (previously returned `None`
  unless `return_string=True`). The `return_string` constructor argument has
  been removed — use `plot_gen.to_string()` / `plot_to_string()` for string
  output. Bounds set explicitly (or via interactive pan/zoom) are now *pinned*
  and preserved across data updates, while all other bounds keep auto-ranging.
- Upgraded mypy to v2.1.0 and dropped CI support for Python 3.8 and 3.9 (EOL).
### Fixed
- A style-only update on a `plot_gen` (e.g. `update(title=...)` before any data)
  no longer raises `KeyError`.
- Explicitly-set bounds are no longer wrongly carried over when the data type
  changes between updates (e.g. switching from numeric to datetime values).
- Upgraded dependencies to resolve dependabot warning on pytest /
  CVE-2025-71176. This only affects uniplot developers, not users.

## [0.22.0] - 2026-05-18
### Added
- 3-5x speed improvement when plotting 1M+ lines using
  [Numba JIT compilation](https://numba.pydata.org/). Numba is an optional
  dependency, that can be installed using `pip install uniplot[fast]`.

```
             ++ v0.9.1   xx v0.21.5   oo current
   Sample size versus plotting time, dots + lines, log-log
┌────────────────────────────────────────────────────────────┐
│                                                          ++│
│                                                        ++  │
│                                                     +++    │
│                                                  +++     xx│
│                                                ++      xx  │
│                                             +++     xxx   o│ 1 s
│                                          +++      xx    oo │
│───────────────────────────────────────+++──────xxx───ooo───│
│                                    +++      xxx   ooo      │
│                                ++++      xxx    ooo        │
│++++                       +++++       xxxx   ooo           │
│    +++++++++++++++++++++++         xxx    ooo              │
│                                 xxx    ooo                 │ 10^-2 s
│                            xxxxx    ooo                    │
│                      xxxxxx   oooooo                       │
│ xxxooooooooooooooooooooooooooo                             │
│oooo                                                        │
└────────────────────────────────────────────────────────────┘
 1               100             10^4             10^6
             ++ v0.9.1   xx v0.21.5   oo v0.22.0
```

## [0.21.5] - 2026-01-04
### Added
- Python 3.14 to the CI pipeline.
- Adds better categories and keywords to the PyPI config.

## [0.21.4] - 2025-08-03
### Added
- Adds `histogram_to_string` to output histogram plot as string. Thanks to
  @stodoran for the suggestion and PR!
- The `color` option now also supports a single named color, though it outputs
  a warning.

## [0.21.3] - 2025-07-27
### Added
- Adds the `rounded_corners` option, for round corners of the bounding box.
### Fixed
- Fixes an issue with floating-point axis labels that did not have the correct
  number of digits because they were not rounded correctly.

## [0.21.2] - 2025-06-10
### Added
- Experimental: Support for 3 ways to move in interactive mode: Vim-style,
  arrow keys and FPS-style.
- Example widget, to illustrate how to (one of multiple ways) build
  interactive applications on top of uniplot.

## [0.21.1] - 2025-05-25
### Fixed
- Removed debugging output.

## [0.21.0] - 2025-05-25
### Added
- Support for colored gridlines with the options `x_gridlines_color` and
  `y_gridlines_color`.
- Support for horizontally placed legend labels with the `legend_placement`
  option.
### Fixed
- Width is now exact when y axis labels are disabled.

## [0.20.1] - 2025-05-10
### Added
- Added `x_labels` and `y_labels` options to disable axis labels.
### Fixed
- Fixed black and white terminal colors.

## [0.20.0] - 2025-05-10
### Added
- Support for RGB colors, by passing tuples with red, green and blue values to the
`color` option.
- Support for specifying colors in hexadecimal format, for example `"#ff0000"`.
- Support for color themes, when specifying a single string as the `color` option.
- Support for Python 3.12 and 3.13.

## [0.19.0] - 2025-04-26
### Improved
- Improved line drawing performance 5-10x.

```
     Sample size versus plotting time, dots only, log-log
┌────────────────────────────────────────────────────────────┐
│                                                           +│
│                                                         ++ │
│───────────────────────────────────────────────────────++──x│
│                                                      +  xx │
│                                                    ++  x   │ 0.1 s
│                                                  ++  xx    │
│                                               +++   x      │
│                                            +++    xx       │
│  +++++++++                            +++++     xxx        │
│++         ++++++++++++++++++++++++++++        xx           │
│                                             xx             │ 10^-2 s
│                                            x               │
│                                        xxxx                │
│                                    xxxx                    │
│                             xxxxxxx                        │
│xxxxxx       xxxxxxxxxxxxxxxx                               │ 10^-3 s
│      xxxxxxx                                               │
└────────────────────────────────────────────────────────────┘
 1               100             10^4             10^6
                          ++ v0.9.1
                          xx current

   Sample size versus plotting time, dots + lines, log-log
┌────────────────────────────────────────────────────────────┐
│                                                          ++│
│                                                        ++  │ 10 s
│                                                     +++    │
│                                                  +++    xxx│
│                                                ++     xx   │
│                                             +++    xxx     │ 1 s
│                                          +++    xxx        │
│───────────────────────────────────────+++─────xx───────────│
│                                    +++     xxx             │ 0.1 s
│                                ++++     xxx                │
│++++                       +++++     xxxx                   │
│    +++++++++++++++++++++++       xxx                       │
│                               xxx                          │ 10^-2 s
│                             xx                             │
│                          xxx                               │
│           xxxxxxxxxxxxxxx                                  │ 10^-3 s
│xxxxxxxxxxx                                                 │
└────────────────────────────────────────────────────────────┘
 1               100             10^4             10^6
                          ++ v0.9.1
                          xx current
```

### Changed
- Merged the `force_ascii` feature into the `character_set` option. ASCII character
  plotting can now be done via `character_set="ascii"`. This deprecates the
  `force_ascii` option.

## [0.18.1] - 2025-04-24
### Fixed
- Packaging fixed after the move to uv, as per issues #44 and #46. Thanks to @hmvege
  for pointing this out and providing a PR with the fix.

## [0.18.0] - 2025-04-18
### Improved
- Performance improvements now for all character sets, so for ASCII and Braille
  characters as well.
### Changed
- Switched to [uv](https://docs.astral.sh/uv/) for dependency and build management.

## [0.17.1] - 2025-03-09
### Fixed
- Fixed view reset in interactive mode.
- Fixed incorrect reset after keypress in interactive mode when using legend labels.

## [0.17.0] - 2025-03-08
### Improved
- Significant performance improvements using batch logic. Plotting is up to 33x faster
  for sparse plots. See PRs #40 and #42 on GitHub for details. Thanks a lot to
  @PabloRuizCuevas for providing ideas, pull request and iterating on it!
### Fixed
- `plot_gen` crashed when no options changed in a new iteration. Thanks to
  @PabloRuizCuevas for pointing this out!

## [0.16.3] - 2025-02-09
### Fixed
- Fixed center alignment of titles or legend labels that are longer than the hard cap.

## [0.16.2] - 2024-12-18
### Improved
- Simplified example scripts, and added comments for readability.
- Improved Readability of the Readme.

### Fixed
- Gridlines were not displayed when using Braille characters.
- Legend labels are now drawn correctly when using the Braille character set.

## [0.16.1] - 2024-12-07
### Fixed
- Fixed datetime labels with non-zero-aligned start time.

## [0.16.0] - 2024-12-07
### Added
- Examples folder.
- Added `plot_gen` function to support streaming use cases, and streaming
  example script. Thanks to @PabloRuizCuevas for idea and PR!

## [0.15.1] - 2024-11-03
### Fixed
- Fixed naming of Block Elements Unicode character option.

## [0.15.0] - 2024-11-03
### Added
- Support for plotting with Braille characters (8x resolution, and a lighter
  look) using the `character_set` option.

### Improved
- Introduced linting with Ruff.
- Switched to Ruff for code formatting.
- Full CI is now executed on GitHub, same as locally.

## [0.14.1] - 2024-08-18
### Improved
- Stricter label overlap filter leading to higher quality datetime labels.
- Shortened, more readable datetime labels when plotting over months/years.

## [0.14.0] - 2024-08-17
### Improved
- Much improved datetime labels. Still experimental, but now using a similar
  logic as the numerical labels.

## [0.13.1] - 2024-07-06
### Added
- New option `force_ascii_characters` that controls the symbols to be used, so
  that we can plot multiple series even without Unicode or color.

### Fixed
- Legend labels were colored even with the option `color=False`. Thanks to
  @NikosAlexandris for pointing this out!

## [0.13.0] - 2024-06-08
### Added
- Basic color control: The `color` option can now also accept a list of
  strings. Thanks to @PabloRuizCuevas for idea and PR!

## [0.12.8] - 2024-06-07
### Improved
- Make plot lines appear simultaneously. This can be important when collecting
  various terminal streams, for example in a log analyzer. Thanks to
  @PabloRuizCuevas for idea and PR!

## [0.12.7] - 2024-05-22
### Fixed
- Fixed passing partially empty series. Thanks to @PabloRuizCuevas for pointing
  this out!

## [0.12.6] - 2024-05-04
### Fixed
- Fixed bin range default check when plotting a histogram. Thanks to @riga for
  the PR!

## [0.12.5] - 2024-03-24
### Fixed
- Link from PyPI to the GitHub repository was missing. Thanks to @adigitoleo
  for pointing this out!
- Histogram limits are now auto-expanded for both sides (minimum and maximum)
  independently, which just makes more sense.

## [0.12.4] - 2024-03-13
### Fixed
- Limits to bins that are passed to the histogram function via `bins_min` and
  `bins_max` now work as expected. Thanks to @riga for pointing this out!

## [0.12.3] - 2024-03-05
### Fixed
- Vertical and horizontal lines that were partially out of view were not drawn
  fully. Fixed thanks to @riga

## [0.12.2] - 2024-02-23
### Added
- Experimental: Added support for plotting the y-axis as timestamps.
- Explicit conversion to string of text options. The goal here is to allow for
  other objects to be passed in, such as a machine learning model object,
  without manually creating the text label first.

## [0.12.1] - 2024-02-17
### Changed
- Nicer datetime label formatting.

## [0.12.0] - 2024-02-17
### Added
- Added tests to make sure uniplot works well with [Polars](https://pola.rs/).
- Experimental: Added support for plotting the x-axis as timestamps. Thanks to
  @leighleighleigh for the first draft!

## [0.11.0] - 2024-01-14
### Changed
- Improved tolerance to invalid values when plotting logarithmic scales.

## [0.10.2] - 2023-09-02
### Fixed
- Fixed plotting of grouped Pandas DataFrames, and added tests for it.

## [0.10.1] - 2023-08-03
### Fixed
- Plotting now silently ignores negative or zero values during logarithmic
  plotting.

## [0.10.0] - 2023-03-06
### Added
- New option to force ASCII mode, for example for CI/CD systems that do not
  support Unicode.
### Fixed
- Added `__all__` statement to fix language server complaint when using `from
  uniplot import plot` thanks to @h0uter

## [0.9.2] - 2023-02-19
### Changed
- Vertical axis labels with equal line spacing are now preferred, for a cleaner
  look.
- Fixed many of the rare cases with blank axis labels.

## [0.9.1] - 2023-01-24
### Fixed
- Labels are now correctly aligned to zero.
- Manual view options are now working correctly when using log scales.

## [0.9.0] - 2023-01-19
### Added
- Data can now be plotted on a logarithmic scale.

### Fixed
- Fixed a rare issue with displaying the wrong number of digits of axis labels.

## [0.8.1] - 2022-12-19
### Security
- Upgraded NumPy, and then Python to >= 3.8 with it, to avoid allowing older
  NumPy versions with known vulnerabilities.

## [0.8.0] - 2022-10-29
### Changed
- Switched to Poetry for package and build management.
- Now using `numpy.typing` for type hints of NumPy objects, which means that
  uniplot now supports NumPy versions `>=1.20.0`.

## [0.7.0] - 2022-09-22
### Changed
- Improved NaN tolerance: Lines will not be plotted when connecting points that
  contain NaN values in the coordinates.

## [0.6.0] - 2022-09-11
### Changed
- NaN values in the input series will now be silently ignored, for ease of use.

### Fixed
- Centering of x-axis labels with units.

## [0.5.0] - 2021-12-02
### Added
- Axis labels can now have units.
- New option to put a hard cap on the line length.

## [0.4.4] - 2021-05-15
### Added
- New print_to_string function to return a string instead of printing to
  stdout.

## [0.4.3] - 2021-04-07
### Added
- t.b.d.
