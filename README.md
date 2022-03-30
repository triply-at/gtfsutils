# gtfsutils

[![](https://img.shields.io/pypi/v/gtfsutils.svg)](https://pypi.python.org/pypi/gtfsutils)

GTFS command-line tool and Python GTFS utility library

# Installation

To install the package, type:

```bash
pip install gtfsutils
```

# Usage

The usage is illustrated in [quickstart.ipynb](quickstart.ipynb).

The package can be also used as a command-line tool. Here is how to filter a GTFS file using a bounding box:

```bash
gtfsutils filter \
  --verbose \
  --bounds "[16.197, 47.999, 16.549, 48.301]" \
  -i data/vienna.gtfs.zip \
  -o data/vienna-filtered.gtfs.zip
```

Here is how to compute the bounding box of a GTFS file:

```bash
gtfsutils bounds -i data/vienna.gtfs.zip
```

For more information on the command-line interface, type:

```bash
gtfsutils --help
```

```
usage: gtfsutils [-h] [-i SRC] [-o DST] [--bounds BOUNDS] [-f OPERATION] [--overwrite] [-v] method

GTFS Utilities

positional arguments:
  method                GTFS method: filter, bounds, merge

optional arguments:
  -h, --help            show this help message and exit
  -i SRC, --input SRC   Input filepath
  -o DST, --output DST  Output filepath
  --bounds BOUNDS       Filter boundary
  -f OPERATION, --filter-operation OPERATION
                        Filter operation (within, intersects)
  --overwrite           Overwrite if exists
  -v, --verbose         Verbose output
```

# License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) for details.
