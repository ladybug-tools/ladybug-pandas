import pytest

import pandas as pd

from ladybug.datatype.temperature import DryBulbTemperature
from ladybug.datatype.energyintensity import DirectNormalRadiation
from ladybug.epw import EPW

from ladybug_pandas.extension_types.dtype import LadybugDType
from ladybug_pandas.extension_types.arraytype import LadybugArrayType

from ladybug_pandas import DataFrame, Series

@pytest.fixture(scope='session')
def epw():
    epw_path = 'tests/assets/epw/tokyo.epw'

    epw = EPW(epw_path)

    epw._import_data()

    return epw

@pytest.fixture()
def temp_series(epw):
    return Series(epw.dry_bulb_temperature)

@pytest.fixture()
def dnr_series(epw):
    return Series(epw.direct_normal_radiation)


def test_addition(temp_series, dnr_series):
    res = temp_series + dnr_series

    # should not raise


def test_conversion(temp_series):

    array = temp_series.values

    new_array = array.to_ip()

    # should not raise


def test_from_collections(epw):

    df = DataFrame([epw.dry_bulb_temperature, epw.direct_normal_radiation])

    # should not raise

def test_from_epw(epw):

    df = DataFrame.from_epw(epw)

    # should not raise

def test_si_from_si(temp_series):

    equality_values = temp_series.ladybug.to_si() == temp_series

    assert equality_values.all()