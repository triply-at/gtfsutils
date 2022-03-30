# gtfsutils

GTFS command-line tool and Python GTFS utility library

## Installation

```bash
git clone git@github.com:triply-at/gtfsutils.git
cd gtfsutils
pip install .
```

## Usage

```bash
gtfsutils -h
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
