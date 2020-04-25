from typing import List, Union
import pandas as pd
import numpy as np
from ladybug.datacollection import HourlyDiscontinuousCollection, HourlyContinuousCollection, \
    DailyCollection, MonthlyCollection, MonthlyPerHourCollection, BaseCollection
from ladybug.epw import EPW
from .extension_types.arraytype import LadybugArrayType

def dataframe_from_collections(
    data_collections: List[Union[HourlyDiscontinuousCollection, HourlyContinuousCollection, DailyCollection, MonthlyCollection, MonthlyPerHourCollection]],
    name_key: str = None,
) -> pd.DataFrame:
    
    data_collection_type = None

    df = pd.DataFrame()

    for collection in data_collections:
        # Check they are data collections
        assert isinstance(collection, BaseCollection), \
            f'All items of data_collections must be a type of ladybug data collection, not: {type(collection)}'

        # Assert same type of data collection
        if data_collection_type is None:
            data_collection_type = type(collection)
        else:
            assert isinstance(collection, data_collection_type), \
                f'All items of data_collections must be of the same type of data collection. Found {data_collection_type} and {type(collection)}'


        # Create columns from collections
        array = LadybugArrayType._from_data_collection(collection)

        if name_key is not None:
            col_name = collection.header.metadata[name_key]
        else:
            col_name = collection.header.data_type.name

        data = {}

        data[col_name] = array

        temp_df = pd.DataFrame(
            data=data,
            index=collection.datetimes
        )

        df = pd.concat([df, temp_df], axis=1)

    return df


def dataframe_from_epw(
    epw: EPW
):
    df = dataframe_from_collections(epw._data[6:])

    df = df.replace(999999999.0, np.nan)

    return df
