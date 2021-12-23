import pandas as pd
from collections import defaultdict
from . import (
    load_gtfs,
    COLUMNS_DEPENDENCY_DICT,
    AVAILABLE_GTFS_FILES
)


def merge_gtfs(src):
    gtfs_list = []
    if all(isinstance(elem, str) for elem in src):
        for filepath in src:
            gtfs_list.append(load_gtfs(filepath))
    elif all(isinstance(elem, list) for elem in src):
        gtfs_list = src
    else:
        raise ValueError(
            f"Data type not supported: {type(src)}")

    id_offset_dict = defaultdict(int)
    col_map_dict = {}

    # Assign new ids
    for df_dict in gtfs_list:
        for col, (id_col, deps) in COLUMNS_DEPENDENCY_DICT.items():
            col_map_dict[col] = {v: i + id_offset_dict[col] for i, v in enumerate(
                df_dict[col][id_col].values)}
            df_dict[col][id_col] = df_dict[col][id_col] \
                .apply(col_map_dict[col].get)
            
            id_offset_dict[col] += len(col_map_dict[col])

            for dep in deps:
                df_dict[dep][id_col] = df_dict[dep][id_col] \
                    .apply(col_map_dict[col].get)

    # Merge dataframes
    df_dict_combined = {}
    for key in AVAILABLE_GTFS_FILES:
        if any(key in df_dict for df_dict in gtfs_list):
            df_list = [df_dict[key] for df_dict in gtfs_list if key in df_dict]
            df_dict_combined[key] = pd.concat(df_list)

    # Validate id columns (TODO: move to test)
    for col, (id_col, deps) in COLUMNS_DEPENDENCY_DICT.items():
        assert df_dict_combined[col][id_col].isna().sum() == 0, \
            f"has NaN for {col} {id_col}"
        if col != 'shapes':
            assert df_dict_combined[col][id_col].is_unique, \
                f"not unique for {col} {id_col}"
            assert df_dict_combined[col][id_col].is_monotonic, \
                f"not monotonic for {col} {id_col}"

        for dep in deps:
            assert df_dict_combined[dep][id_col].isna().sum() == 0, \
                f"has NaN for dep {dep} {id_col}"

    return df_dict_combined
