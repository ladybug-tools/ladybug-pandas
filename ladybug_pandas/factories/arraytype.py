from pandas.api.extensions import ExtensionArray, ExtensionDtype
from typing import Sequence, Any
from pandas._typing import ArrayLike
import numpy as np
import pandas as pd

import operator

from pandas.api.extensions import ExtensionArray, ExtensionDtype, ExtensionScalarOpsMixin
from typing import Sequence, Any, Union
from pandas.core.dtypes.generic import ABCExtensionArray

from pandas._typing import ArrayLike
import numpy as np
import pandas as pd

from ladybug_pandas.arraytype import LadybugArrayType

def LadybugArrayFactory(ladybug_dtype):

    class_attributes = {
        "_dtype": ladybug_dtype,
    }

    return type(
        f'{ladybug_dtype.__class__.name}Array',
        (LadybugArrayType,),
        class_attributes
    )
