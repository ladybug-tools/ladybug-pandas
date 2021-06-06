import pandas as pd
import pytest
from ladybug.datatype.energyintensity import DirectNormalRadiation
from ladybug.datatype.temperature import DryBulbTemperature
from ladybug.epw import EPW
from ladybug_pandas import DataFrame, Series
from ladybug_pandas.extension_types.arraytype import LadybugArrayType
from ladybug_pandas.extension_types.dtype import LadybugDType


@pytest.fixture(scope='session')
def epw():
    epw_path = 'tests/assets/epw/tokyo.epw'

    epw = EPW(epw_path)

    epw._import_data()

    return epw


@pytest.fixture
def temp_list(epw):
    return list(epw.dry_bulb_temperature.values)


@pytest.fixture
def dnr_list(epw):
    return list(epw.direct_normal_radiation.values)


@pytest.fixture()
def temp_series(epw):
    return Series(epw.dry_bulb_temperature)


@pytest.fixture()
def dnr_series(epw):
    return Series(epw.direct_normal_radiation)


def test_addition(temp_series, dnr_series, temp_list, dnr_list):
    res = temp_series + dnr_series
    addition_list = []
    for i, v in enumerate(temp_list):
        addition_list.append(v + dnr_list[i])
    assert res.tolist() == addition_list


def test_conversion(temp_series):
    array = temp_series.values
    new_array = array.to_ip()
    assert new_array[0] == 37.58


def test_from_collections(epw):
    df = DataFrame([epw.dry_bulb_temperature, epw.direct_normal_radiation])
    # should not raise


def test_from_epw_with_loaded_data(epw):
    df = DataFrame.from_epw(epw)
    # should not raise


def test_from_epw_without_loaded_data(epw):
    epw_path = 'tests/assets/epw/tokyo.epw'
    epw = EPW(epw_path)
    df = DataFrame.from_epw(epw)


def test_si_from_si(temp_series):
    equality_values = temp_series.ladybug.to_si() == temp_series
    assert equality_values.all()
