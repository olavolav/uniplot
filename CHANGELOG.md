# Changelog

All notable changes to uniplot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unrelease
### Fixed
- Labels were not correctly aligned to zero.
- Manual view options are now working correctly when using log scales.

## [0.9.0] - 2023-01-19
### Added
- Data can now be plotted on logarithmic scale.

### Fixed
- Fixed a rare issue with displaying the wrong number of digits of axis labels.

## [0.8.1] - 2022-12-19
### Security
- Upgraded NumPy, and then Python to >= 3.8 with it, to avoid allowing older NumPy versions with known vulnerabilites.

## [0.8.0] - 2022-10-29
### Changed
- Switched to Poetry for package and build management.
- Now using `numpy.typing` for type hints of NumPy objects, which means that uniplot now support numpy versions `>=1.20.0`.

## [0.7.0] - 2022-09-22
### Changed
- Improved NaN tolerance: Lines will not be plotted when connecting points that contain NaN values in the coordinates.

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
