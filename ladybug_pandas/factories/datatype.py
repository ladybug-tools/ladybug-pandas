from typing import Sequence, Any
from pandas.api.extensions import ExtensionArray, ExtensionDtype
from pandas._typing import ArrayLike
import pandas as pd
import numpy as np

from ladybug.datatype.base import DataTypeBase

from ladybug_pandas.arraytype import LadybugArrayType


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
        "construct_array_type": construct_array_type,
        "kind": 'f',

    }

    extension_type = type(
        f'{klass.__name__}Type',
        (ExtensionDtype,),
        class_dict
    )

    return pd.api.extensions.register_extension_dtype(extension_type)

