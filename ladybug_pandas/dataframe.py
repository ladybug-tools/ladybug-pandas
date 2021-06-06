from typing import List, Union

import numpy as np
import pandas as pd
from ladybug.datacollection import (BaseCollection, DailyCollection,
                                    HourlyContinuousCollection,
                                    HourlyDiscontinuousCollection,
                                    MonthlyCollection,
                                    MonthlyPerHourCollection)
from ladybug.epw import EPW

from .extension_types.arraytype import LadybugArrayType


class DataFrame:

    """Generate a Dataframe from a list of ladybug data collections

    Example:
        .. code-block:: python

            import ladybug_pandas as lbp
            from ladybug.wea import Wea
            from ladybug.location import Location

            location = Location(
                city='Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch',
                state='Wales',
                country='United Kingdom',
                latitude=53.224622,
                longitude=-4.197995,
                time_zone=0
            )

            wea = Wea.from_ashrae_clear_sky(location=location)

            df = lbp.DataFrame([
                wea.direct_normal_irradiance,
                wea.diffuse_horizontal_irradiance,
                wea.global_horizontal_irradiance,
                wea.direct_horizontal_irradiance,
            ])

    Arguments:
        data_collections {List[Union[HourlyDiscontinuousCollection, HourlyContinuousCollection, DailyCollection, MonthlyCollection, MonthlyPerHourCollection]]} -- A list of datacollections. Must all be of the same type

    Keyword Arguments:
        name_key {str} -- The name of the metadata key to use as a column name. Will default to datatype name if not specified (default: {None})

    Returns:
        pd.DataFrame -- A pandas dataframe. Each column will have a type of LadybugArrayType
    """

    def __new__(
        cls,
        data_collections: List[Union[HourlyDiscontinuousCollection, HourlyContinuousCollection, DailyCollection, MonthlyCollection, MonthlyPerHourCollection]],
        name_key: str = None,
        populate_metadata: bool = False,
        axis: int = 1,
    ) -> pd.DataFrame:

        data_collection_type = None

        df_list = []

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

            if populate_metadata:
                for k, v in collection.header.metadata.items():
                    data[k] = [v] * array.__len__()

            df_list.append(pd.DataFrame(
                data=data,
                index=collection.datetimes
            ))

        df = pd.concat(df_list, axis=axis)

        return df

    @classmethod
    def from_epw(
        cls,
        epw: EPW
    ) -> pd.DataFrame:
        """Generate a Dataframe from an EPW object

        Example:
            .. code-block:: python

                import ladybug_pandas as lbp
                from ladybug.epw import EPW

                epw_path = 'tests/assets/epw/tokyo.epw'

                epw = EPW(epw_path)

                df = lbp.DataFrame.from_epw(epw)

        Arguments:
            epw {EPW} -- A ladybug EPW object

        Returns:
            pd.DataFrame -- A pandas dataframe. Each column will have a type of LadybugArrayType
        """
        if not epw.is_data_loaded:
            epw._import_data()

        df = cls(epw._data[6:])

        df = df.replace(999999999.0, np.nan)

        return df
