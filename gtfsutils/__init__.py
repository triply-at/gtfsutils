import os
from numpy.lib.arraysetops import isin
import pandas as pd
import shapely.geometry
import geopandas as gpd
from zipfile import ZipFile

__version__ = "0.0.1"


REQUIRED_GTFS_FILES = [
    'agency',
    'stops',
    'routes',
    'trips',
    'calendar',
    'stop_times',
    #'shapes',
    #'frequencies',
    #'feedinfo'
]

# https://developers.google.com/transit/gtfs/reference
AVAILABLE_GTFS_FILES = [
    "agency",
    "stops",
    "routes",
    "trips",
    "stop_times",
    "calendar",
    "calendar_dates",
    "fare_attributes",
    "fare_rules",
    "shapes",
    "frequencies",
    "transfers",
    "pathways",
    "levels",
    "feed_info",
    "translations",
    "attributions"
]

ROUTE_TYPE_MAP = {
    0: 'tram, light_rail',
    1: 'subway',
    2: 'rail, railway, train',
    3: 'bus, ex-bus',
    4: 'ferry',
    5: 'cableCar',
    6: 'gondola',
    7: 'funicular'
}

COLUMNS_DEPENDENCY_DICT = {
    'agency':   ('agency_id',  ['routes']),
    'routes':   ('route_id',   ['trips']),
    'trips':    ('trip_id',    ['stop_times']),
    'stops':    ('stop_id',    ['stop_times']),
    'calendar': ('service_id', ['calendar_dates']),
    'shapes':   ('shape_id',   ['trips'])
}


def load_gtfs(filepath, subset=None):
    df_dict = {}
    if os.path.isdir(filepath):
        for filename in os.listdir(filepath):
            filekey = filename.split('.txt')[0]
            if (subset is None) or (filekey in subset):
                df_dict[filekey] = pd.read_csv(
                    os.path.join(filepath, filename),
                    low_memory=False)
    else:
        with ZipFile(filepath) as z:
            for filename in z.namelist():
                filekey = filename.split('.txt')[0]
                if (subset is None) or (filekey in subset):
                    df_dict[filekey] = pd.read_csv(
                        z.open(filename),
                        low_memory=False)
            
    return df_dict


def load_shapes(src):
    if isinstance(src, str):
        df_dict = load_gtfs(src, subset=['shapes'])
    elif isinstance(src, dict):
        df_dict = src
    else:
        raise ValueError(
            f"Data type not supported: {type(src)}")
    
    items = []
    for shape_id, g in df_dict['shapes'].groupby('shape_id'):
        g = g.sort_values('shape_pt_sequence')
        coords = g[['shape_pt_lon', 'shape_pt_lat']].values

        if len(coords) > 1:    
            items.append({
                'shape_id': shape_id,
                'geom': shapely.geometry.LineString(coords)
            })

    return gpd.GeoDataFrame(
        items, geometry='geom', crs="EPSG:4326")


def save_gtfs(df_dict, filepath, ignore_required=False, overwrite=False):
    if not ignore_required and not all(key in df_dict.keys() 
               for key in REQUIRED_GTFS_FILES):
        raise ValueError("Not all required GTFS files in dictionary")
    
    if overwrite or not os.path.exists(filepath):
        with ZipFile(filepath, "w") as zf:
            for filekey, df in df_dict.items():
                buffer = df.to_csv(index=False)
                zf.writestr(filekey + ".txt", buffer)


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


def filter_gtfs(df_dict, filter_geometry, operation='within'):
    if isinstance(filter_geometry, list):
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

    # Filter transfers.txt
    if 'transfers' in df_dict:
        mask = df_dict['transfers']['from_stop_id'].isin(stop_ids) \
            & df_dict['transfers']['to_stop_id'].isin(stop_ids)
        df_dict['transfers'] = df_dict['transfers'][mask]


def get_bounding_box(src):
    if isinstance(src, str):
        df_dict = load_gtfs(src, subset=['stops'])
    elif isinstance(src, dict):
        df_dict = src
    else:
        raise ValueError(
            f"Data type not supported: {type(src)}")

    return [
        df_dict['stops']['stop_lon'].min(),
        df_dict['stops']['stop_lat'].min(),
        df_dict['stops']['stop_lon'].max(),
        df_dict['stops']['stop_lat'].max()
    ]
