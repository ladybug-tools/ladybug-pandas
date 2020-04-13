import pytest

import pandas as pd

from ladybug.datatype.temperature import DryBulbTemperature
from ladybug.datatype.energyintensity import DirectNormalRadiation
from ladybug.epw import EPW
from ladybug_pandas.factories.datatype import LadybugTypeFactory, LadybugDtypeFactory
from ladybug_pandas.factories.arraytype import LadybugArrayFactory

@pytest.fixture()
def temp_array(dtype):
    return LadybugArrayFactory(dtype)

@pytest.fixture()
def dnr_array():
    dnr_type = LadybugTypeFactory(DirectNormalRadiation)

    dnr_dtype = LadybugDtypeFactory(dnr_type)

    return LadybugArrayFactory(dnr_dtype())

@pytest.fixture()
def epw():
    epw_path = 'tests/assets/epw/tokyo.epw'

    return EPW(epw_path)

@pytest.fixture()
def temp_series(temp_array, epw):
    return pd.Series(temp_array(epw.dry_bulb_temperature))

@pytest.fixture()
def dnr_series(dnr_array, epw):
    return pd.Series(dnr_array(epw.direct_normal_radiation))


def test_addition(temp_series, dnr_series):
    res = temp_series + dnr_series

    print(res)
    print(type(res.array))

    # assert False