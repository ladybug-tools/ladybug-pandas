from copy import deepcopy
from typing import Any, Sequence, Union

import numpy as np
import pandas as pd
from ladybug.datacollection import BaseCollection
from pandas._typing import ArrayLike
from pandas.api.extensions import (ExtensionArray, ExtensionDtype,
                                   ExtensionScalarOpsMixin)
from pandas.core.dtypes.generic import ABCExtensionArray
from scipy import stats

from .dtype import LadybugDType

COMPARISON_OPS = ['eq', 'ne', 'lt', 'gt', 'le', 'ge']


class LadybugArrayType(ExtensionArray, ExtensionScalarOpsMixin):

    _dtype = LadybugDType()

    def __init__(self, values, dtype=None, copy=False):

        # self._dtype = dtype
        if dtype is not None:
            if isinstance(dtype, str):
                # Will raise error if not right
                self._dtype.construct_from_string(dtype)
            else:
                self._dtype = dtype

        if isinstance(dtype, ExtensionDtype) or dtype is None:
            values = np.asarray(values, dtype=np.float_)
        elif isinstance(values, LadybugArrayType):
            values = values.data
            self._dtype = values.dtype
        else:
            values = np.asarray(values)
            self._dtype = values.dtype

        # TODO: dtype?
        if copy:
            values = values.copy()
            self._dtype = deepcopy(self._dtype)
            # if isinstance(self._dtype, LadybugDType):
            #     self._dtype = copy.deepcopy(self._dtype)

        self.data = values

    @classmethod
    def _from_sequence(cls, scalars: Sequence, dtype=None, copy=False):
        """
        Construct a new ExtensionArray from a sequence of scalars.
        Parameters
        ----------
        scalars : Sequence
            Each element will be an instance of the scalar type for this
            array, ``cls.dtype.type``.
        dtype : dtype, optional
            Construct for this particular dtype. This should be a Dtype
            compatible with the ExtensionArray.
        copy : bool, default False
            If True, copy the underlying data.
        Returns
        -------
        ExtensionArray
        """
        if dtype is None:
            if isinstance(scalars, cls):
                dtype = scalars.dtype
            elif isinstance(scalars, list) and isinstance(scalars[0], np.bool_):
                dtype = np.dtype("bool")
            else:
                dtype = None

        return cls(scalars, dtype=dtype, copy=copy)

    @classmethod
    def _from_sequence_of_strings(cls, strings, dtype=None, copy=False):
        """
        Construct a new ExtensionArray from a sequence of strings.
        .. versionadded:: 0.24.0
        Parameters
        ----------
        strings : Sequence
            Each element will be an instance of the scalar type for this
            array, ``cls.dtype.type``.
        dtype : dtype, optional
            Construct for this particular dtype. This should be a Dtype
            compatible with the ExtensionArray.
        copy : bool, default False
            If True, copy the underlying data.
        Returns
        -------
        ExtensionArray
        """
        return cls([float(string) for string in strings], dtype=dtype, copy=copy)

    @classmethod
    def _from_factorized(cls, values, original):
        """
        Reconstruct an ExtensionArray after factorization.
        Parameters
        ----------
        values : ndarray
            An integer ndarray with the factorized values.
        original : ExtensionArray
            The original ExtensionArray that factorize was called on.
        See Also
        --------
        factorize
        ExtensionArray.factorize
        """
        dtype = None

        if isinstance(original, cls):
            dtype = original.dtype
        elif isinstance(original, list):
            dtype = original[0].dtype
        else:
            raise f'Original value of type {type(original)} not supported'

        return cls(values, dtype)

    @classmethod
    def _from_data_collection(cls, datacollection: BaseCollection):
        """Generate a Ladybug Array from a Ladybug DataCollection

        Arguments:
            datacollection {BaseCollection} -- A ladybug data collection

        Returns:
            LadybugArrayType -- A Ladybug Array
        """
        dtype = LadybugDType.construct_from_header(datacollection.header)

        return cls(values=datacollection.values, dtype=dtype)

    # def to_hourly_discontinuous_collection(self, datetimes: List[DateTime]) -> HourlyDiscontinuousCollection:
    #     assert len(self.data) == len(datetimes), f'Datetime index of length {len(datetimes)} does not match length of array {len(self)}'

    #     return HourlyDiscontinuousCollection(
    #         header=self.dtype.to_header(),
    #         values=self.data.tolist(),
    #         datetimes=datetimes,
    #     )

    def convert_to_unit(self, unit: str):
        """Convert the Data Collection to the input unit

        Arguments:
            unit {str} -- A unit string that exists for the data type
        """
        self.data = self.dtype.data_type.to_unit(
            self.data, unit, self.dtype.unit)
        self.dtype.unit = unit

    def convert_to_ip(self):
        """Convert the Data Collection to IP units."""
        self.data, self.dtype.unit = self.dtype.data_type.to_ip(
            self.data, self.dtype.unit)

    def convert_to_si(self):
        """Convert the Data Collection to SI units."""
        self.data, self.dtype.unit = self.dtype.data_type.to_si(
            self.data, self.dtype.unit)

    def to_unit(self, unit):
        """Return a Data Collection in the input unit

        Arguments:
            unit {str} -- A unit string that exists for the data type

        Returns:
            LadybugArrayType -- A Ladybug Array converted to the desired unit
        """
        new_data_c = self.copy()
        new_data_c.convert_to_unit(unit)
        return new_data_c

    def to_ip(self):
        """Return a Data Collection in IP units

        Returns:
            LadybugArrayType -- A Ladybug Array converted to the desired unit
        """
        new_data_c = self.copy()
        new_data_c.convert_to_ip()
        return new_data_c

    def to_si(self):
        """Return a Data Collection in SI units

        Returns:
            LadybugArrayType -- A Ladybug Array converted to the desired unit
        """
        new_data_c = self.copy()
        new_data_c.convert_to_si()
        return new_data_c

    def __getitem__(self, item):
        # type (Any) -> Any
        """
        Select a subset of self.
        Parameters
        ----------
        item : int, slice, or ndarray
            * int: The position in 'self' to get.
            * slice: A slice object, where 'start', 'stop', and 'step' are
              integers or None
            * ndarray: A 1-d boolean NumPy ndarray the same length as 'self'
        Returns
        -------
        item : scalar or ExtensionArray
        Notes
        -----
        For scalar ``item``, return a scalar value suitable for the array's
        type. This should be an instance of ``self.dtype.type``.
        For slice ``key``, return an instance of ``ExtensionArray``, even
        if the slice is length 0 or 1.
        For a boolean mask, return an instance of ``ExtensionArray``, filtered
        to the values where ``item`` is True.
        """
        if isinstance(item, int):
            datum = self.data[item]
            return self.data[item]
        elif isinstance(item, slice):
            pass
        elif isinstance(item, np.ndarray):
            if item.dtype == bool and len(item) != len(self):
                raise IndexError(
                    f'Boolean index has wrong length: {item.size} instead of {self.data.size}')
        elif isinstance(item, list):
            try:
                item = np.asarray(item, dtype=np.int_)
            except Exception as e:
                raise ValueError(
                    "Cannot index with an integer indexer containing NA values")

        elif isinstance(item, pd.core.arrays.boolean.BooleanArray):
            if len(item) != len(self):
                raise IndexError(
                    f'Boolean index has wrong length: {len(item)} instead of {len(self)}')

            item = item.to_numpy(dtype="bool", na_value=False)
        elif isinstance(item, pd.core.arrays.integer.IntegerArray):
            try:
                item = item.to_numpy(dtype="int", na_value=pd.NA)
            except Exception as e:
                raise ValueError(
                    "Cannot index with an integer indexer containing NA values")
        else:
            raise IndexError(f'Item type note recognised {type(item)}')

        view = self.view()
        view.data = view.data[item]

        return view

    def __arrow_array__(self, type=None):
        # convert the underlying array values to a pyarrow Array
        import pyarrow as pa
        return pa.array(self.data, type=pa.float64())

    def __len__(self) -> int:
        """
        Length of this array
        Returns
        -------
        length : int
        """
        return self.data.size

    def __setitem__(self, key: Union[int, np.ndarray], value: Any) -> None:
        """
        Set one or more values inplace.

        This method is not required to satisfy the pandas extension array
        interface.

        Parameters
        ----------
        key : int, ndarray, or slice
            When called from, e.g. ``Series.__setitem__``, ``key`` will be
            one of

            * scalar int
            * ndarray of integers.
            * boolean ndarray
            * slice object

        value : ExtensionDtype.type, Sequence[ExtensionDtype.type], or object
            value or values to be set of ``key``.

        Returns
        -------
        None
        """
        # Some notes to the ExtensionArray implementor who may have ended up
        # here. While this method is not required for the interface, if you
        # *do* choose to implement __setitem__, then some semantics should be
        # observed:
        #
        # * Setting multiple values : ExtensionArrays should support setting
        #   multiple values at once, 'key' will be a sequence of integers and
        #  'value' will be a same-length sequence.
        #
        # * Broadcasting : For a sequence 'key' and a scalar 'value',
        #   each position in 'key' should be set to 'value'.
        #
        # * Coercion : Most users will expect basic coercion to work. For
        #   example, a string like '2018-01-01' is coerced to a datetime
        #   when setting on a datetime64ns array. In general, if the
        #   __init__ method coerces that value, then so should __setitem__
        # Note, also, that Series/DataFrame.where internally use __setitem__
        # on a copy of the data.

        if isinstance(key, pd.core.arrays.BooleanArray):
            key = key.fillna(False)
            key = key.to_numpy(dtype="bool")
        elif isinstance(key, pd.core.arrays.IntegerArray):
            try:
                key = key.to_numpy(dtype="int")
            except ValueError as error:
                if 'Specify an appropriate \'na_value\'' in str(error):
                    raise ValueError(
                        'Cannot index with an integer indexer containing NA values')
                raise error

        elif isinstance(key, list):
            list_type = None
            list_item = 0

            while list_item < len(key):
                if isinstance(key[list_item], int):
                    list_type = "int"
                    break
                elif isinstance(key[list_item], bool):
                    list_type = "bool"
                    break
                else:
                    list_item += 1

            assert list_type is not None, IndexError(
                'arrays used as indices must be of integer (or boolean) type')

            try:
                key = np.asarray(key, dtype=list_type)
            except TypeError as error:
                if 'int() argument must be a string, a bytes-like object or a number, not \'NAType\'' in str(error):
                    raise ValueError(
                        'Cannot index with an integer indexer containing NA values')

                raise error

            if list_type == 'bool':
                key = key.fillna(False)

        try:
            self.data[key] = value
        except IndexError as error:
            if "boolean index did not match indexed array along dimension" in str(error):
                raise IndexError('wrong length: ' + str(error))
            else:
                raise error

    # def __add__(self, other):

    #     if isinstance(other, self.__class__):
    #         self.data += other.data

    #     elif isinstance(other, (float, int, np.array)):
    #         self.data += other

    #     # elif isi

    @property
    def dtype(self) -> ExtensionDtype:
        """
        An instance of 'ExtensionDtype'.
        """
        return self._dtype
        # if self._dtype is None:
        #     return self.data.dtype
        # else:
        #     return self._dtype

    @property
    def nbytes(self) -> int:
        """
        The number of bytes needed to store this object in memory.
        """
        # If this is expensive to compute, return an approximate lower bound
        # on the number of bytes needed.
        # return self._itemsize * self.__len__
        return self.data.nbytes

    @property
    def _ndarray(self):
        return self.data

    def _reduce(self, name, skipna=True, **kwargs):
        """
        Return a scalar result of performing the reduction operation.
        Parameters
        ----------
        name : str
            Name of the function, supported values are:
            { any, all, min, max, sum, mean, median, prod,
            std, var, sem, kurt, skew }.
        skipna : bool, default True
            If True, skip NaN values.
        **kwargs
            Additional keyword arguments passed to the reduction function.
            Currently, `ddof` is the only supported kwarg.
        Returns
        -------
        scalar
        Raises
        ------
        TypeError : subclass does not define reductions
        """

        root = np

        child_kwargs = {}

        if 'ddof' in kwargs:
            child_kwargs['ddof'] = kwargs['ddof']

        if name == 'kurt':
            child_kwargs['bias'] = False
            name = 'kurtosis'
            root = stats

        if name == 'skew':
            child_kwargs['bias'] = False
            root = stats

        if skipna is True:
            # return getattr(self.data[~np.isnan(self.data)], name)(**child_kwargs)
            return getattr(root, name)(self.data[~np.isnan(self.data)], **child_kwargs)
        else:
            # return getattr(self.data, name)(**child_kwargs)
            return getattr(root, name)(self.data, **child_kwargs)

    def isna(self) -> ArrayLike:
        """
        A 1-D array indicating if each value is missing.
        Returns
        -------
        na_values : Union[np.ndarray, ExtensionArray]
            In most cases, this should return a NumPy ndarray. For
            exceptional cases like ``SparseArray``, where returning
            an ndarray would be expensive, an ExtensionArray may be
            returned.
        Notes
        -----
        If returning an ExtensionArray, then
        * ``na_values._is_boolean`` should be True
        * `na_values` should implement :func:`ExtensionArray._reduce`
        * ``na_values.any`` and ``na_values.all`` should be implemented
        """
        return np.isnan(self.data)

    def value_counts(self, dropna=True):
        """
        Return a Series containing counts of unique values.

        Parameters
        ----------
        dropna : bool, default True
            Don't include counts of NaT values.

        Returns
        -------
        Series
        """
        from pandas import Index, Series

        if dropna:
            values = self[~self.isna()].data
        else:
            values = self.data

        unique, counts = np.unique(values, return_counts=True)

        return Series(counts, index=unique, dtype="int64")

    def take(
        self, indices: Sequence[int], allow_fill: bool = False, fill_value: Any = None
    ) -> "ExtensionArray":
        """
        Take elements from an array.
        Parameters
        ----------
        indices : sequence of int
            Indices to be taken.
        allow_fill : bool, default False
            How to handle negative values in `indices`.
            * False: negative values in `indices` indicate positional indices
              from the right (the default). This is similar to
              :func:`numpy.take`.
            * True: negative values in `indices` indicate
              missing values. These values are set to `fill_value`. Any other
              other negative values raise a ``ValueError``.
        fill_value : any, optional
            Fill value to use for NA-indices when `allow_fill` is True.
            This may be ``None``, in which case the default NA value for
            the type, ``self.dtype.na_value``, is used.
            For many ExtensionArrays, there will be two representations of
            `fill_value`: a user-facing "boxed" scalar, and a low-level
            physical NA value. `fill_value` should be the user-facing version,
            and the implementation should handle translating that to the
            physical version for processing the take if necessary.
        Returns
        -------
        ExtensionArray
        Raises
        ------
        IndexError
            When the indices are out of bounds for the array.
        ValueError
            When `indices` contains negative values other than ``-1``
            and `allow_fill` is True.
        See Also
        --------
        numpy.take
        api.extensions.take
        Notes
        -----
        ExtensionArray.take is called by ``Series.__getitem__``, ``.loc``,
        ``iloc``, when `indices` is a sequence of values. Additionally,
        it's called by :meth:`Series.reindex`, or any other method
        that causes realignment, with a `fill_value`.
        Examples
        --------
        Here's an example implementation, which relies on casting the
        extension array to object dtype. This uses the helper method
        :func:`pandas.api.extensions.take`.
        .. code-block:: python
           def take(self, indices, allow_fill=False, fill_value=None):
               from pandas.core.algorithms import take
               # If the ExtensionArray is backed by an ndarray, then
               # just pass that here instead of coercing to object.
               data = self.astype(object)
               if allow_fill and fill_value is None:
                   fill_value = self.dtype.na_value
               # fill value should always be translated from the scalar
               # type for the array, to the physical storage type for
               # the data, before passing to take.
               result = take(data, indices, fill_value=fill_value,
                             allow_fill=allow_fill)
               return self._from_sequence(result, dtype=self.dtype)
        """
        # Implementer note: The `fill_value` parameter should be a user-facing
        # value, an instance of self.dtype.type. When passed `fill_value=None`,
        # the default of `self.dtype.na_value` should be used.
        # This may differ from the physical storage type your ExtensionArray
        # uses. In this case, your implementation is responsible for casting
        # the user-facing type to the storage type, before using
        # pandas.api.extensions.take
        copy = self.copy()
        copy.data = pd.api.extensions.take(
            copy.data, indices, allow_fill=allow_fill, fill_value=fill_value)

        return copy

    def copy(self) -> "ExtensionArray":
        """
        Return a copy of the array.
        Returns
        -------
        ExtensionArray
        """
        # return self.__class__._from_factorized(self.data.copy(), self)
        return self.__class__(
            values=self.data.copy(),
            dtype=self.dtype,
            copy=True,
        )

    def view(self, dtype=None) -> Union[ABCExtensionArray, np.ndarray]:
        """
        Return a view on the array.

        Parameters
        ----------
        dtype : str, np.dtype, or ExtensionDtype, optional
            Default None.

        Returns
        -------
        ExtensionArray
            A view of the :class:`ExtensionArray`.
        """
        # NB:
        # - This must return a *new* object referencing the same data, not self.
        # - The only case that *must* be implemented is with dtype=None,
        #   giving a view with the same dtype as self.
        if dtype is not None:
            raise NotImplementedError(dtype)

        return self.__class__._from_factorized(self.data, self)

    @classmethod
    def _concat_same_type(
        cls, to_concat: Sequence["ExtensionArray"]
    ) -> "ExtensionArray":
        """
        Concatenate multiple array.
        Parameters
        ----------
        to_concat : sequence of this type
        Returns
        -------
        ExtensionArray
        """
        data = np.concatenate([ga.data for ga in to_concat])
        return cls._from_factorized(data, to_concat)

    def astype(self, dtype, copy=True):
        if isinstance(dtype, self.dtype.__class__):
            if copy:
                return self.copy()
            return self

        # return np.array(self.data, dtype=dtype, copy=copy)
        return super(LadybugArrayType, self).astype(dtype)


LadybugArrayType._add_arithmetic_ops()
LadybugArrayType._add_comparison_ops()
