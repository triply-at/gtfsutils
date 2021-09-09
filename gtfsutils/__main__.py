import json
import time
import logging
import argparse
import shapely.geometry
from . import (
    load_shapes, load_gtfs, save_gtfs
)


def filter_extent(src_filepath, dst_filepath, bounds, ):
    print(src_filepath, dst_filepath, bounds)

    t = time.time()
    df_dict = load_gtfs(src_filepath)
    duration = time.time() - t
    logging.debug(f"Loaded {src_filepath} for {duration:.2f}s")

    # Filter shapes
    t = time.time()
    gdf_shapes = load_shapes(src_filepath)
    duration = time.time() - t
    logging.debug(f"Loaded {src_filepath} shapes geometry for {duration:.2f}s")
    bbox = shapely.geometry.box(*bounds)
    mask = gdf_shapes.within(bbox)
    gdf_shapes = gdf_shapes[mask]

    # Filter shapes.txt
    shape_ids = gdf_shapes['shape_id'].values
    mask = df_dict['shapes']['shape_id'].isin(shape_ids)
    df_dict['shapes'] = df_dict['shapes'][mask]
    
    # Filter trips.txt
    mask = df_dict['trips']['shape_id'].isin(shape_ids)
    df_dict['trips'] = df_dict['trips'][mask]
    
    # Filter route.txt
    route_ids = df_dict['trips']['route_id'].values
    mask = df_dict['routes']['route_id'].isin(route_ids)
    df_dict['routes'] = df_dict['routes'][mask]
    
    # Filter agency.txt
    agency_ids = df_dict['routes']['agency_id'].values
    mask = df_dict['agency']['agency_id'].isin(agency_ids)
    df_dict['agency'] = df_dict['agency'][mask]

    # Filter stop_times.txt
    trip_ids = df_dict['trips']['trip_id'].values
    mask = df_dict['stop_times']['trip_id'].isin(trip_ids)
    df_dict['stop_times'] = df_dict['stop_times'][mask]

    # Filter stops.txt
    stop_ids = df_dict['stop_times']['stop_id'].values
    mask = df_dict['stops']['stop_id'].isin(stop_ids)
    df_dict['stops'] = df_dict['stops'][mask]

    # Save filtered GTFS
    t = time.time()
    save_gtfs(df_dict, dst_filepath, ignore_required=True)
    logging.debug(f"Saved {dst_filepath} for {duration:.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description="GTFS Utilities")
    parser.add_argument(action='store',
        dest='src', help="Input filepath")
    parser.add_argument(action='store',
        dest='dst', help="Output filepath")
    parser.add_argument("--bounds", action='store',
        dest='bounds', help="Filter boundary")
    parser.add_argument('-v', '--verbose', action='store_true',
        dest='verbose', default=False,
        help="Verbose output")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s-%(levelname)s-%(message)s',
        level=log_level)

    bounds = json.loads(args.bounds)
    filter_extent(args.src, args.dst, bounds)


if __name__ == '__main__':
    main()
