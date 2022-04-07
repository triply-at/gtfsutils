import shapely
import numpy as np
from . import load_shapes


def filter_by_geometry(df_dict, filter_geometry, operation='within'):
    if isinstance(filter_geometry, list) or isinstance(filter_geometry, np.ndarray):
        if len(filter_geometry) != 4:
            raise ValueError("Wrong dimension of bounds")
        geom = shapely.geometry.box(*filter_geometry)
    elif isinstance(filter_geometry, shapely.geometry.base.BaseGeometry):
        geom = filter_geometry
    else:
        raise ValueError(
            f"filter_geometry type {type(filter_geometry)} not supported!")
    
    # Filter shapes
    gdf_shapes = load_shapes(df_dict)
    if operation == 'within':
        mask = gdf_shapes.within(geom)
    elif operation == 'intersects':
        mask = gdf_shapes.intersects(geom)
    else:
        raise ValueError(
            f"Operation {operation} not supported!")
        
    gdf_shapes = gdf_shapes[mask]
    shape_ids = gdf_shapes['shape_id'].values
    filter_by_shape_ids(df_dict, shape_ids)


def filter_by_shape_ids(df_dict, shape_ids):
    # Filter shapes.txt
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

    # Filter transfers.txt
    if 'transfers' in df_dict:
        mask = df_dict['transfers']['from_stop_id'].isin(stop_ids) \
             & df_dict['transfers']['to_stop_id'].isin(stop_ids)
        df_dict['transfers'] = df_dict['transfers'][mask]


def filter_by_agency_ids(df_dict, agency_ids):
    # Filter agency.txt
    mask = df_dict['agency']['agency_id'].isin(agency_ids)
    df_dict['agency'] = df_dict['agency'][mask]

    # Filter routes.txt
    mask = df_dict['routes']['agency_id'].isin(agency_ids)
    df_dict['routes'] = df_dict['routes'][mask]

    # Filter trips.txt
    routes_ids = df_dict['routes']['route_id']
    mask = df_dict['trips']['route_id'].isin(routes_ids)
    df_dict['trips'] = df_dict['trips'][mask]

    # Filter stop_times.txt
    trips_ids = df_dict['trips']['trip_id']
    mask = df_dict['stop_times']['trip_id'].isin(trips_ids)
    df_dict['stop_times'] = df_dict['stop_times'][mask]

    # Filter stops.txt
    stops_ids = df_dict['stop_times']['stop_id'].values
    mask = df_dict['stops']['stop_id'].isin(stops_ids)
    df_dict['stops'] = df_dict['stops'][mask]

    # Filter shapes.txt
    shapes_ids = df_dict['trips']['shape_id'].values
    mask = df_dict['shapes']['shape_id'].isin(shapes_ids)
    df_dict['shapes'] = df_dict['shapes'][mask]

    # Filter transfers.txt
    if 'transfers' in df_dict:
        mask = df_dict['transfers']['from_stop_id'].isin(stops_ids) \
             & df_dict['transfers']['to_stop_id'].isin(stops_ids)
        df_dict['transfers'] = df_dict['transfers'][mask]
