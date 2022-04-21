import json
import time
import logging
import argparse
from . import (
    load_gtfs,
    save_gtfs,
    get_bounding_box,
    print_info
)
from .filter import filter_by_geometry


def main():
    parser = argparse.ArgumentParser(
        description="GTFS Utilities")
    parser.add_argument(action='store',
        dest='method', help="GTFS method: filter, bounds, info, merge")
    parser.add_argument("-i", "--input", action='store',
        dest='src', help="Input filepath")
    parser.add_argument("-o", "--output", action='store',
        dest='dst', help="Output filepath")
    parser.add_argument("--bounds", action='store',
        dest='bounds', help="Filter boundary")
    parser.add_argument("-f", "--filter-operation", action='store',
        dest='operation', help="Filter operation (within, intersects)",
        default="within")
    parser.add_argument("--overwrite", action='store_true',
        dest='overwrite', help="Overwrite if exists")
    parser.add_argument('-v', '--verbose', action='store_true',
        dest='verbose', default=False,
        help="Verbose output")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_level)

    if args.method == "filter":
        assert args.bounds is not None, "No bounds defined"
        assert args.src is not None, "No input file specified"
        assert args.dst is not None, "No output file specified"

        # Prepare bounds
        bounds = json.loads(args.bounds)

        # Load GTFS
        t = time.time()
        df_dict = load_gtfs(args.src)
        duration = time.time() - t
        logging.debug(f"Loaded {args.src} in {duration:.2f}s")

        # Filter GTFS
        t = time.time()
        filter_by_geometry(df_dict, bounds, operation=args.operation)
        duration = time.time() - t
        logging.debug(f"Filtered {args.src} in {duration:.2f}s")

        # Save filtered GTFS
        t = time.time()
        save_gtfs(df_dict, args.dst, ignore_required=True, overwrite=args.overwrite)
        duration = time.time() - t
        logging.debug(f"Saved to {args.dst} in {duration:.2f}s")
    
    elif args.method == "bounds":
        assert args.src is not None, "No input file specified"

        bounds = get_bounding_box(args.src)
        print(bounds)
    
    elif args.method == "info":
        assert args.src is not None, "No input file specified"
        print_info(args.src)

    elif args.method == "merge":
        raise NotImplementedError("Merge not implemented")


if __name__ == '__main__':
    main()
