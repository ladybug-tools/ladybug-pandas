import pandas as pd

from ..extension_types.arraytype import LadybugArrayType


@pd.api.extensions.register_series_accessor("ladybug")
class LadybugSeriesAccessor:

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    @property
    def is_lb_array(self):
        return isinstance(self._obj.values, LadybugArrayType)

    def check_type(self):
        assert self.is_lb_array, \
            f'Cannort perform ladybug operation on Array of type {type(self._obj.values)}'

    def to_si(self):
        self.check_type()
        return pd.Series(self._obj.values.to_si(), index=self._obj.index)

    def to_ip(self):
        self.check_type()
        return pd.Series(self._obj.values.to_ip(), index=self._obj.index)

    def to_unit(self, unit):
        self.check_type()
        return pd.Series(self._obj.values.to_unit(unit), index=self._obj.index)


@pd.api.extensions.register_dataframe_accessor("ladybug")
class LadybugDataFrameAccessor:

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def to_si(self):
        return self._obj.apply(lambda x: x.ladybug.to_si() if x.ladybug.is_lb_array else x)

    def to_ip(self):
        return self._obj.apply(lambda x: x.ladybug.to_ip() if x.ladybug.is_lb_array else x)

    def to_unit(self, unit):
        return self._obj.apply(lambda x: x.ladybug.to_unit(unit) if x.ladybug.is_lb_array else x)
