import re
import types

import numpy as np
from ladybug.datatype import TYPESDICT
from ladybug.datatype.base import DataTypeBase
from ladybug.header import Header
from pandas.api.extensions import ExtensionDtype, register_extension_dtype


def _to_unit_base_hack(self, base_unit, values, unit, from_unit):
    """Return values in a given unit given the input from_unit."""
    namespace = {'self': self, 'values': values}
    if not from_unit == base_unit:
        self.is_unit_acceptable(from_unit, True)
        statement = 'self._{}_to_{}(values)'.format(
            self._clean(from_unit), self._clean(base_unit))
        values = eval(statement, namespace)
    if not unit == base_unit:
        self.is_unit_acceptable(unit, True)
        statement = 'self._{}_to_{}(values)'.format(
            self._clean(base_unit), self._clean(unit))
        values = eval(statement, namespace)
    return values


def _is_numeric_hack(*args, **kwargs):
    return True


funcType = types.MethodType


@register_extension_dtype
class LadybugDType(ExtensionDtype):

    _metadata = ('data_type_name', 'unit')

    def __init__(self, data_type=None, unit=None):

        if data_type is None and unit is None:
            self.data_type = DataTypeBase('Undefined Type')
            self.unit = 'None'
        else:
            assert isinstance(data_type, DataTypeBase), ValueError(
                f'{data_type} is not an instance of type DataTypeBase')
            assert unit in data_type._units, ValueError(
                f'unit {unit} should be one of {data_type.units}')

            # Replace to unit base function to work with numpy arrays

            self.data_type = data_type
            self.unit = unit

        # setattr(self.data_type, '_is_numeric', _is_numeric_hack)
        # self.data_type._to_unit_base = _to_unit_base_hack.__get__()
        self.data_type._to_unit_base = funcType(
            _to_unit_base_hack, self.data_type)

    @classmethod
    def construct_from_string(cls, string):
        if not isinstance(string, str):
            raise TypeError(
                "'construct_from_string' expects a string, got {}".format(
                    type(string))
            )

        match = re.fullmatch(r"(.*) \((.*)\)", string)

        if match is None:
            raise TypeError(
                "Cannot construct a 'LadybugDType' from '{}'".format(string)
            )

        type_name = ''.join(match[1].split(' '))
        unit = match[2]

        assert type_name in TYPESDICT, ValueError(
            f'Ladybug Type of {type_name} is not recognized')
        data_type = TYPESDICT[type_name]()

        assert unit in data_type._units, ValueError(
            f'Ladybug Type unit of {unit} is not recognized for type {type_name}')

        return cls(data_type=data_type, unit=unit)

    @classmethod
    def construct_array_type(cls):
        from .arraytype import LadybugArrayType

        return LadybugArrayType

    @classmethod
    def construct_from_header(cls, header: Header):
        """[summary]

        Arguments:
            header {Header} -- [description]

        Returns:
            [type] -- [description]
        """
        return cls(data_type=header.data_type, unit=header.unit)

    def to_header(self):
        """Cast the ExtensionDtyp to a ladybug header object

        Returns:
            Header -- A ladybug header object
        """
        return Header(
            data_type=self.data_type,
            unit=self.unit
        )

    @property
    def type(self):
        return np.float

    @property
    def _is_numeric(self):
        return True

    @property
    def kind(self):
        return 'f'

    @property
    def name(self):
        # return "{} ({})".format(self.data_type, self.unit)
        return self.__repr__()

    @property
    def data_type_name(self):
        return self.data_type.name

    def __repr__(self):
        return "{} ({})".format(self.data_type_name, self.unit)
