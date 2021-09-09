import os
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
    'feedinfo'
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


def save_gtfs(df_dict, filepath, ignore_required=False):
    if not ignore_required and not all(key in df_dict.keys() 
               for key in REQUIRED_GTFS_FILES):
        raise ValueError("Not all required GTFS files in dictionary")
    
    with ZipFile(filepath, "w") as zf:
        for filekey, df in df_dict.items():
            buffer = df.to_csv(index=False)
            zf.writestr(filekey + ".txt", buffer)


def load_routes_counts(filepath):
    df_dict = load_gtfs(filepath, subset=[
        'agency', 'routes', 'trips', 'stops', 'stop_times'
    ])
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
    
    def get_route_geometry(group):
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

    df_trip_shape = pd.merge(
        df_stop_times[['stop_id', 'route_id', 'stop_sequence', 'counts']], 
        df_stops[['stop_id', 'stop_lon', 'stop_lat']],
        how='left', on='stop_id')
    df_trip_geometry = df_trip_shape \
        .groupby('route_id') \
        .apply(get_route_geometry)
    df_trip_geometry = df_trip_geometry.reset_index()

    df = pd.merge(
        df_routes,
        df_trip_geometry,
        on='route_id', how='left')
    
    return gpd.GeoDataFrame(
        df, geometry='geometry', crs="EPSG:4326")

        
def load_shapes(filepath):
    df_dict = load_gtfs(filepath, subset=['shapes'])
    
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
