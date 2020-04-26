import pandas as pd
from .extension_types.arraytype import LadybugArrayType

def series_from_collection(data_collection) -> pd.Series:
    """Generate a pandas Series from a Ladybug Data Collection

    Arguments:
        data_collection {ladybug._datacollectionbase.BaseCollection} -- An instance of a ladybug data collection

    Returns:
        pd.Series -- A pandas Series of type Ladybug Array
    """

    array = LadybugArrayType._from_data_collection(collection)

    return pd.Series(
        data=array,
        index=collection.datetimes
    )