# Changelog

All notable changes to uniplot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
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
