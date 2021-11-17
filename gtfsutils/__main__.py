import json
import time
import logging
import argparse
from . import load_gtfs, save_gtfs, filter_gtfs


def main():
    parser = argparse.ArgumentParser(
        description="GTFS Utilities")
    parser.add_argument(action='store',
        dest='src', help="Input filepath")
    parser.add_argument(action='store',
        dest='dst', help="Output filepath")
    parser.add_argument("--bounds", action='store',
        dest='bounds', help="Filter boundary")
    parser.add_argument("-o", "--operation", action='store',
        dest='operation', help="Filter operation (within, intersects)")
    parser.add_argument("--overwrite", action='store_true',
        dest='overwrite', help="Overwrite if exists")
    parser.add_argument('-v', '--verbose', action='store_true',
        dest='verbose', default=False,
        help="Verbose output")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s-%(levelname)s-%(message)s',
        level=log_level)

    bounds = json.loads(args.bounds)
    src_filepath = args.src
    dst_filepath = args.dst

    # Load GTFS
    t = time.time()
    df_dict = load_gtfs(src_filepath)
    duration = time.time() - t
    logging.debug(f"Loaded {src_filepath} for {duration:.2f}s")

    # Filter GTFS
    t = time.time()
    filter_gtfs(df_dict, bounds, operation=args.operation)
    duration = time.time() - t
    logging.debug(f"Filtered {src_filepath} for {duration:.2f}s")

    # Save filtered GTFS
    t = time.time()
    save_gtfs(df_dict, dst_filepath, ignore_required=True, overwrite=args.overwrite)
    duration = time.time() - t
    logging.debug(f"Saved {dst_filepath} for {duration:.2f}s")


if __name__ == '__main__':
    main()
