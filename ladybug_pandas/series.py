import pandas as pd
from .extension_types.arraytype import LadybugArrayType

def series_from_collection(data_collection) -> pd.Series:
    array = LadybugArrayType._from_data_collection(collection)

    return pd.Series(
        data=array,
        index=collection.datetimes
    )