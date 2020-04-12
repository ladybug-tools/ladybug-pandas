from typing import Sequence, Any
from pandas.api.extensions import ExtensionArray, ExtensionDtype
from pandas._typing import ArrayLike
import pandas as pd
import numpy as np

from ladybug.datatype.base import DataTypeBase

from ladybug.datatype.temperature import Temperature

from ladybug_pandas.arraytype import LadybugArrayType

# class LadybugDtype(ExtensionDtype):
    
#     type = DataTypeBase()
#     name = "base"
#     _is_numeric = True

#     @classmethod
#     def construct_from_string(cls, string):
#         if not isinstance(string, str):
#             raise TypeError(
#                 "'construct_from_string' expects a string, got {}".format(type(string))
#             )
#         elif string == cls.name:
#             return cls()
#         else:
#             raise TypeError(
#                 "Cannot construct a '{}' from '{}'".format(cls.__name__, string)
#             )


def LadybugTypeFactory(cls):
    """Class factory for ladyug datatype class to work with pandas
    
    Arguments:
        cls {Class} -- A ladybug datatype class
    
    Returns:
        class -- A pandas compliant ladybug datatype class
    """

    def _is_numeric(values):
        pass

    def _to_unit_base(self, base_unit, values, unit, from_unit):
        pass

    class_dict = {
        "_is_numeric": _is_numeric,
        "_to_unit_base": _to_unit_base
    }

    return type(
        cls.__name__,
        (cls,),
        class_dict,
    )

def LadybugDtypeFactory(klass):

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

    @classmethod
    def construct_array_type(cls):
        return LadybugArrayType


    lb_class_instance = klass()

    class_dict = {
        "type": np.float_,
        "name": klass.__name__,
        "_is_numeric": True,
        # "construct_from_string": construct_from_string,
        "construct_array_type": construct_array_type,
        "kind": 'f',
        # "_record_type": np.dtype([('hi', '>u8'), ('lo', '>u8')])

    }

    extension_type = type(
        f'{klass.__name__}Type',
        (ExtensionDtype,),
        class_dict
    )

    return pd.api.extensions.register_extension_dtype(extension_type)

