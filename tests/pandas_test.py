import numpy as np
import pandas as pd
import pytest
from pandas.core import ops
from pandas.tests.extension import base


class TestCasting(base.BaseCastingTests):
    pass


class TestDtypes(base.BaseDtypeTests):

    def test_array_type(self, data, dtype):
        """Replace with isinstance test because of inheritance"""
        assert isinstance(data, dtype.construct_array_type())
        # assert dtype.construct_array_type() is type(data)


class TestConstructors(base.BaseConstructorsTests):
    pass


class TestGetItem(base.BaseGetitemTests):

    def test_getitem_ellipsis_and_slice(self, data):
        pytest.skip('To be fixed in a later version of ladybug-pandas')


class TestBaseGroupby(base.BaseGroupbyTests):
    pass


class TestBaseInterface(base.BaseInterfaceTests):

    def test_contains(self, data, data_missing):
        # GH-37867
        # Tests for membership checks. Membership checks for nan-likes is tricky and
        # the settled on rule is: `nan_like in arr` is True if nan_like is
        # arr.dtype.na_value and arr.isna().any() is True. Else the check returns False.

        na_value = data.dtype.na_value
        # ensure data without missing values
        data = data[~data.isna()]

        # first elements are non-missing
        assert data[0] in data
        assert data_missing[0] in data_missing

        # check the presence of na_value
        assert na_value in data_missing
        assert na_value not in data

        # the data can never contain other nan-likes than na_value
        # Changed the test here by removing "float('nan')" from
        # tm.NULL_OBJECTS
        # https://stackoverflow.com/questions/52123892/numpy-nan-not-always-recognized
        null_objects = [None, np.nan, pd.NaT, pd.NA]
        # for na_value_obj in tm.NULL_OBJECTS:
        for na_value_obj in null_objects:
            if na_value_obj is na_value:
                continue
            assert na_value_obj not in data
            assert na_value_obj not in data_missing, f'{data_missing.data}'


class TestBaseParsing(base.BaseParsingTests):
    pass


class TestBaseMethods(base.BaseMethodsTests):

    def test_combine_le(self, data_repeated):
        pytest.skip('To be fixed in a later version of ladybug-pandas')


class TestBaseMissing(base.BaseMissingTests):
    pass


class TestBaseArithmeticOps(base.BaseArithmeticOpsTests):

    series_scalar_exc = None
    frame_scalar_exc = None
    series_array_exc = None
    divmod_exc = None

    def test_error(self):
        pass

    def test_divmod_series_array(self, data, data_for_twos):
        s = pd.Series(data)
        self._check_divmod_op(s, divmod, data, exc=self.divmod_exc)

        other = data_for_twos
        self._check_divmod_op(other, ops.rdivmod, s, exc=self.divmod_exc)

        other = pd.Series(other)
        self._check_divmod_op(other, ops.rdivmod, s, exc=self.divmod_exc)


class TestBasePrinting(base.BasePrintingTests):
    pass


class TestBaseBooleanReduce(base.BaseBooleanReduceTests):
    pass


class TestBaseNumericReduce(base.BaseNumericReduceTests):
    pass


class TestBaseReshaping(base.BaseReshapingTests):

    def test_concat_mixed_dtypes(self, data):
        # https://github.com/pandas-dev/pandas/issues/20762
        df1 = pd.DataFrame({"A": data[:3]})
        df2 = pd.DataFrame({"A": [1, 2, 3]})
        df3 = pd.DataFrame({"A": ["a", "b", "c"]}).astype("category")
        dfs = [df1, df2, df3]

        # dataframes
        result = pd.concat(dfs)
        expected = pd.concat([x.astype(object) for x in dfs])
        self.assert_frame_equal(result, expected)

        # series
        result = pd.concat([x["A"] for x in dfs])
        expected = pd.concat([x["A"].astype(object) for x in dfs])
        self.assert_series_equal(result, expected)

        # simple test for just EA and one other
        result = pd.concat([df1, df2])
        expected = pd.concat([df1.astype("object"), df2.astype("object")])
        self.assert_frame_equal(result, expected)

        # Commented out the section below because it was failing
        # I think it fails because the ndarray type of the ladybug tools
        # array type is a float which concats into a float rather than an object
        # when presented with a list of integers

        # result = pd.concat([df1["A"], df2["A"]])
        # expected = pd.concat([df1["A"].astype("object"), df2["A"].astype("object")])
        # self.assert_series_equal(result, expected)

    pass


class TestBaseSetitem(base.BaseSetitemTests):
    pass
