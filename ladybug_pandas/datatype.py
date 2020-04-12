import numpy as np
from pandas.api.extensions import ExtensionDtype
from ladybug.datatype.base import DataTypeBase

class LadybugDtype(ExtensionDtype):
    
    # type = DataTypeBase()
    type = np.float_
    name = "base"
    _is_numeric = True

    @classmethod
    def construct_from_string(cls, string):
        if not isinstance(string, str):
            raise TypeError(
                "'construct_from_string' expects a string, got {}".format(type(string))
            )
        elif string == cls.name:
            return cls()
        else:
            raise TypeError(
                "Cannot construct a '{}' from '{}'".format(cls.__name__, string)
            )
