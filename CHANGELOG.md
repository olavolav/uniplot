# Changelog

All notable changes to uniplot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Experimental: Added support for plotting the y axis as timestamps.

## [0.12.1] - 2024-02-17
### Changed
- Nicer datetime label formatting.

## [0.12.0] - 2024-02-17
### Added
- Added tests to make sure uniplot works well with [Polars](https://pola.rs/).
- Experimental: Added support for plotting the x axis as timestamps.

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
- Data can now be plotted on logarithmic scale.

### Fixed
- Fixed a rare issue with displaying the wrong number of digits of axis labels.

## [0.8.1] - 2022-12-19
### Security
- Upgraded NumPy, and then Python to >= 3.8 with it, to avoid allowing older
  NumPy versions with known vulnerabilites.

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
- Centering of labels of x axis with units.

## [0.5.0] - 2021-12-02
### Added
- Axis labels can now have units.
- New option to put a hard cap on the line length.

## [0.4.4] - 2021-05-15
### Added
- New print_to_string function to return string instead of printing to stdout.

## [0.4.3] - 2021-04-07
### Added
- t.b.d.
