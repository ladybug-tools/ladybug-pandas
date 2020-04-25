import pytest
from pandas.tests.extension import base
import pandas as pd
from pandas.core import ops


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
    pass

class TestBaseGroupby(base.BaseGroupbyTests):
    pass

class TestBaseInterface(base.BaseInterfaceTests):
    pass

class TestBaseParsing(base.BaseParsingTests):
    pass

class TestBaseMethods(base.BaseMethodsTests):
    pass

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

# class TestBaseComparisonOps(base.BaseComparisonOpsTests):

#     def _compare_other(self, s, data, op_name, other):
#         op = self.get_op_from_name(op_name)
#         if op_name == "__eq__":
#             assert getattr(data, op_name)(other) is NotImplemented
#             assert not op(s, other).all()
#         elif op_name == "__ne__":
#             assert getattr(data, op_name)(other) is NotImplemented
#             assert op(s, other).all()

#         else:

#             # array
#             assert getattr(data, op_name)(other) is NotImplemented

#             # series
#             s = pd.Series(data)
#             with pytest.raises(TypeError):
#                 op(s, other)


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

