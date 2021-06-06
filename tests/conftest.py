import operator

import numpy as np
import pytest
from ladybug.epw import EPW
from ladybug_pandas.extension_types.arraytype import LadybugArrayType
from ladybug_pandas.extension_types.dtype import LadybugDType
from pandas import Series
from pandas.core import ops


@pytest.fixture(scope='session')
def dbt_data_collection():
    epw_path = 'tests/assets/epw/tokyo.epw'

    epw = EPW(epw_path)

    return epw.dry_bulb_temperature


@pytest.fixture(scope='session')
def dtype(dbt_data_collection):
    """A fixture providing the ExtensionDtype to validate."""
    return LadybugDType.construct_from_header(dbt_data_collection.header)


# @pytest.fixture
# def dbt_array(dtype):
#     return LadybugArrayType

@pytest.fixture
def data(dbt_data_collection, dtype):
    """
    Length-100 array for this type.
    * data[0] and data[1] should both be non missing
    * data[0] and data[1] should not be equal
    """

    # values = dbt_data_collection.values[:100]

    # return dbt_array(values)
    # dbt_data_collection.values = dbt_data_collection[:100]

    return LadybugArrayType(dbt_data_collection.values[:100], dtype=dtype)


@pytest.fixture
def data_missing(dtype):
    """Length-2 array with [NA, Valid]"""
    return LadybugArrayType([np.nan, 3.4], dtype=dtype)


@pytest.fixture(params=["data", "data_missing"])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == "data":
        return data
    elif request.param == "data_missing":
        return data_missing


@pytest.fixture
def data_repeated(data):
    """
    Generate many datasets.
    Parameters
    ----------
    data : fixture implementing `data`
    Returns
    -------
    Callable[[int], Generator]:
        A callable that takes a `count` argument and
        returns a generator yielding `count` datasets.
    """

    def gen(count):
        for _ in range(count):
            yield data

    return gen


@pytest.fixture
def data_for_sorting(dtype):
    """
    Length-3 array with a known sort order.
    This should be three items [B, C, A] with
    A < B < C
    """
    return LadybugArrayType([5, 10, 2], dtype=dtype)


@pytest.fixture
def sort_by_key():
    return None


@pytest.fixture
def data_missing_for_sorting(dtype):
    """
    Length-3 array with a known sort order.
    This should be three items [B, NA, A] with
    A < B and NA missing.
    """
    return LadybugArrayType([5, None, 2], dtype=dtype)


@pytest.fixture
def data_for_twos(dtype):
    """Length-100 array in which all the elements are two."""
    return LadybugArrayType([2]*100, dtype=dtype)


@pytest.fixture
def na_cmp():
    """
    Binary operator for comparing NA values.
    Should return a function of two arguments that returns
    True if both arguments are (scalar) NA for your type.
    By default, uses ``operator.is_``
    """
    def comp(a, b):
        return np.isnan(a) and np.isnan(b)

    return comp
    # return operator.is_


@pytest.fixture
def na_value():
    """The scalar missing value for this type. Default 'None'"""
    return np.nan


@pytest.fixture
def data_for_grouping(dtype):
    """
    Data for factorization, grouping, and unique tests.
    Expected to be like [B, B, NA, NA, A, A, B, C]
    Where A < B < C and NA is missing
    """
    return LadybugArrayType([3, 3, None, None, 1, 1, 3, 5], dtype=dtype)


@pytest.fixture(params=[True, False])
def box_in_series(request):
    """Whether to box the data in a Series"""
    return request.param


@pytest.fixture(
    params=[
        lambda x: 1,
        lambda x: [1] * len(x),
        lambda x: Series([1] * len(x)),
        lambda x: x,
    ],
    ids=["scalar", "list", "series", "object"],
)
def groupby_apply_op(request):
    """
    Functions to test groupby.apply().
    """
    return request.param


@pytest.fixture(params=[True, False])
def as_frame(request):
    """
    Boolean fixture to support Series and Series.to_frame() comparison testing.
    """
    return request.param


@pytest.fixture(params=[True, False])
def as_series(request):
    """
    Boolean fixture to support arr and Series(arr) comparison testing.
    """
    return request.param


@pytest.fixture(params=[True, False])
def use_numpy(request):
    """
    Boolean fixture to support comparison testing of ExtensionDtype array
    and numpy array.
    """
    return request.param


@pytest.fixture(params=["ffill", "bfill"])
def fillna_method(request):
    """
    Parametrized fixture giving method parameters 'ffill' and 'bfill' for
    Series.fillna(method=<method>) testing.
    """
    return request.param


@pytest.fixture(params=[True, False])
def as_array(request):
    """
    Boolean fixture to support ExtensionDtype _from_sequence method testing.
    """
    return request.param


# ----------------------------------------------------------------
# Operators & Operations
# ----------------------------------------------------------------
_all_arithmetic_operators = [
    "__add__",
    # "__radd__",
    "__sub__",
    # "__rsub__",
    "__mul__",
    # "__rmul__",
    "__floordiv__",
    # "__rfloordiv__",
    "__truediv__",
    # "__rtruediv__",
    "__pow__",
    # "__rpow__",
    "__mod__",
    # "__rmod__",
]


@pytest.fixture(params=_all_arithmetic_operators)
def all_arithmetic_operators(request):
    """
    Fixture for dunder names for common arithmetic operations.
    """
    return request.param


@pytest.fixture(
    params=[
        operator.add,
        ops.radd,
        operator.sub,
        ops.rsub,
        operator.mul,
        ops.rmul,
        operator.truediv,
        ops.rtruediv,
        operator.floordiv,
        ops.rfloordiv,
        operator.mod,
        ops.rmod,
        operator.pow,
        ops.rpow,
    ]
)
def all_arithmetic_functions(request):
    """
    Fixture for operator and roperator arithmetic functions.

    Notes
    -----
    This includes divmod and rdivmod, whereas all_arithmetic_operators
    does not.
    """
    return request.param


_all_numeric_reductions = [
    "sum",
    "max",
    "min",
    "mean",
    "prod",
    "std",
    "var",
    "median",
    "kurt",
    "skew",
]


@pytest.fixture(params=_all_numeric_reductions)
def all_numeric_reductions(request):
    """
    Fixture for numeric reduction names.
    """
    return request.param


_all_boolean_reductions = ["all", "any"]


@pytest.fixture(params=_all_boolean_reductions)
def all_boolean_reductions(request):
    """
    Fixture for boolean reduction names.
    """
    return request.param


@pytest.fixture(params=["__eq__", "__ne__", "__le__", "__lt__", "__ge__", "__gt__"])
def all_compare_operators(request):
    """
    Fixture for dunder names for common compare operations

    * >=
    * >
    * ==
    * !=
    * <
    * <=
    """
    return request.param


@pytest.fixture(params=["__le__", "__lt__", "__ge__", "__gt__"])
def compare_operators_no_eq_ne(request):
    """
    Fixture for dunder names for compare operations except == and !=

    * >=
    * >
    * <
    * <=
    """
    return request.param


@pytest.fixture(
    params=["__and__", "__rand__", "__or__", "__ror__", "__xor__", "__rxor__"]
)
def all_logical_operators(request):
    """
    Fixture for dunder names for common logical operations

    * |
    * &
    * ^
    """
    return request.param
