from pandas.api.extensions import ExtensionArray, ExtensionDtype
from typing import Sequence, Any
from pandas._typing import ArrayLike
import numpy as np
import pandas as pd

def LadybugArrayFactory(ladybug_dtype):

    def __init__(self, values, dtype=None, copy=False):

        values = np.asarray(values)
        # TODO: dtype?
        if copy:
            values = values.copy()

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
        return cls(values)
        

    def __getitem__(self, idx):
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
        self.data[idx]


    def __len__(self) -> int:
        """
        Length of this array
        Returns
        -------
        length : int
        """
        self.data.size


    @property
    def dtype(self) -> ExtensionDtype:
        """
        An instance of 'ExtensionDtype'.
        """
        return self._dtype

    @property
    def nbytes(self) -> int:
        """
        The number of bytes needed to store this object in memory.
        """
        # If this is expensive to compute, return an approximate lower bound
        # on the number of bytes needed.
        self._itemsize * self.__len__

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
        pass

    def copy(self) -> "ExtensionArray":
        """
        Return a copy of the array.
        Returns
        -------
        ExtensionArray
        """
        return self.__class__._from_factorized(self.data)

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
        return cls._from_factorized(data)

    class_attributes = {
        "__array_priority__": 1000,
        "_dtype": ladybug_dtype(),
        "_itemsize": 16,
        "ndim": 1,
        "can_hold_na": True,
    }

    class_dict = {
        "__init__": __init__,
        "_from_sequence": _from_sequence,
        "_from_sequence_of_strings": _from_sequence_of_strings,
        "_from_factorized": _from_factorized,
        "__getitem__": __getitem__,
        "__len__": __len__,
        "dtype": dtype,
        "nbytes": nbytes,
        "isna": isna,
        "take": take,
        "copy": copy,
        "_concat_same_type": _concat_same_type,
    }

    class_dict.update(class_attributes)

    return type(
        f'{ladybug_dtype().__class__.name}Array',
        (ExtensionArray,),
        class_dict,
    )
