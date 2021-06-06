import pandas as pd

from .extension_types.arraytype import LadybugArrayType


class Series:
    """Generate a pandas Series from a Ladybug Data Collection

    Example:
        .. code-block:: python

            import ladybug_pandas as lbp
            from ladybug.wea import Wea
            from ladybug.location import Location

            location = Location(
                city='Taumatawhakatangi­hangakoauauotamatea­turipukakapikimaunga­horonukupokaiwhen­uakitanatahu',
                state='Porangahau',
                country='New Zealand',
                latitude=-40.3500,
                longitude=176.5500,
                time_zone=12
            )

            wea = Wea.from_ashrae_clear_sky(location=location)

            series = lbp.Series(wea.direct_normal_irradiance)

    Arguments:
        data_collection {ladybug._datacollectionbase.BaseCollection} -- An instance of a ladybug data collection

    Returns:
        pd.Series -- A pandas Series of type Ladybug Array
    """

    def __new__(cls, data_collection) -> pd.Series:

        array = LadybugArrayType._from_data_collection(data_collection)

        return pd.Series(
            data=array,
            index=data_collection.datetimes
        )
