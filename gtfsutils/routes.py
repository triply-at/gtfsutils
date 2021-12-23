import shapely
import pandas as pd
import geopandas as gpd
from . import load_gtfs


def _get_group_route_geometry(group):
    counts = group['counts'].iloc[0]
    X = group.sort_values(by='stop_sequence')[
        ['stop_lon', 'stop_lat']
    ].values
    geom = shapely.geometry.LineString()
    if len(X) > 2:
        geom = shapely.geometry.LineString(X)

    return pd.Series(
        [counts, geom], 
        index=['counts', 'geometry'])


def load_routes_counts(src):
    if isinstance(src, str):
        df_dict = load_gtfs(src, subset=[
            'agency', 'routes', 'trips', 'stops', 'stop_times'
        ])
    elif isinstance(src, dict):
        df_dict = src
    else:
        raise ValueError(
            f"Data type not supported: {type(src)}")
    
    df_trips = df_dict['trips']
    df_stops = df_dict['stops']
    df_stop_times = df_dict['stop_times']
    
    if 'agency' in df_dict:
        df_routes = pd.merge(
            df_dict['routes'][[
                'route_id',
                'route_short_name', 
                'route_long_name',
                'route_type',
                'agency_id'
            ]], 
            df_dict['agency'][[
                'agency_id',
                'agency_name'
            ]], 
            on='agency_id')
    else:
        df_routes = df_dict['routes'][[
            'route_id',
            'route_short_name', 
            'route_long_name',
            'route_type'
        ]]

    df_trips = df_trips.groupby('route_id').apply(
        lambda g: pd.Series([
            g['trip_id'].iloc[0], len(g)
        ], index=['trip_id', 'counts']))
    df_trips = df_trips.reset_index()

    trip_ids = df_trips['trip_id'].unique()
    mask = df_stop_times['trip_id'].isin(trip_ids)
    df_stop_times = df_stop_times[mask]

    trip_ids = df_trips['trip_id'].unique()
    mask = df_stop_times['trip_id'].isin(trip_ids)
    df_stop_times = pd.merge(
        df_trips[['trip_id', 'route_id', 'counts']],
        df_stop_times[mask],
        how='left', on='trip_id')
    
    df_trip_shape = pd.merge(
        df_stop_times[['stop_id', 'route_id', 'stop_sequence', 'counts']], 
        df_stops[['stop_id', 'stop_lon', 'stop_lat']],
        how='left', on='stop_id')
    df_trip_geometry = df_trip_shape \
        .groupby('route_id') \
        .apply(_get_group_route_geometry)
    df_trip_geometry = df_trip_geometry.reset_index()

    df = pd.merge(
        df_routes,
        df_trip_geometry,
        on='route_id', how='left')
    
    return gpd.GeoDataFrame(
        df, geometry='geometry', crs="EPSG:4326")
