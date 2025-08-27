"""Core classes and functions for varmeta."""

from __future__ import annotations

from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

from .vars import Var

T = TypeVar("T")


class Val(Generic[T]):  # NoQA: UP046
    """A value associated with a Var object.

    Attributes:
        data (object): The value data.
        var (Var): The associated Var instance.
    """

    def __init__(self, data: T, var: Var) -> None:
        """Initialize a Val.

        Args:
            data (T): The value data.
            var (Var): The associated Var instance.
        """
        if var.data_type != "object" and type(data).__name__ != var.data_type:
            raise TypeError(f"Expected {var.data_type}, got {type(data)}")
        self.data = data
        self.var = var

    def __repr__(self) -> str:
        """Return a string representation of the Val."""
        return f"Val(data={self.data!r}, var={self.var})"

    def unpack(self) -> list[Val[T]]:
        """Unpack the Val if its Var has components."""
        lst = []
        tuples = self.var.unpack_tuples(self.data)
        for subvar, subval in tuples:
            val: Val[T] = Val(subval, subvar)  # type: ignore
            lst.append(val)
        return lst


# Type-restricted Val subclasses
class IntVal(Val):
    """A Val subclass for integer values."""

    def __init__(self, data: int, var: Var) -> None:
        """Initialize an IntVal.

        Args:
            data (int): The integer value.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, int):
            raise TypeError(f"IntVal expects int data, got {type(data)}")
        super().__init__(data, var)


class FloatVal(Val):
    """A Val subclass for float values."""

    def __init__(self, data: float, var: Var) -> None:
        """Initialize a FloatVal.

        Args:
            data (float): The float value.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, float):
            raise TypeError(f"FloatVal expects float data, got {type(data)}")
        super().__init__(data, var)


class StrVal(Val):
    """A Val subclass for str values."""

    def __init__(self, data: str, var: Var) -> None:
        """Initialize a StrVal.

        Args:
            data (str): The string value.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, str):
            raise TypeError(f"StrVal expects str data, got {type(data)}")
        super().__init__(data, var)


class BoolVal(Val):
    """A Val subclass for bool values."""

    def __init__(self, data: bool, var: Var) -> None:
        """Initialize a BoolVal.

        Args:
            data (bool): The boolean value.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, bool):
            raise TypeError(f"BoolVal expects bool data, got {type(data)}")
        super().__init__(data, var)


class ListVal(Val):
    """A Val subclass for list values."""

    def __init__(self, data: list, var: Var) -> None:
        """Initialize a ListVal.

        Args:
            data (list): The list.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, list):
            raise TypeError(f"ListVal expects list data, got {type(data)}")
        super().__init__(data, var)


class DictVal(Val):
    """A Val subclass for dict values."""

    def __init__(self, data: dict, var: Var) -> None:
        """Initialize a DictVal.

        Args:
            data (dict): The dictionary.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, dict):
            raise TypeError(f"DictVal expects dict data, got {type(data)}")
        super().__init__(data, var)


class NDArrayVal(Val):
    """A Val subclass for numpy array values."""

    def __init__(self, data: NDArray, var: Var) -> None:
        """Initialize a numpy NDArray.

        Args:
            data (NDArray): The array.
            var (Var): The associated Var instance.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(
                f"NumpyArrayVal expects np.ndarray data, got {type(data)}"
            )
        super().__init__(data, var)


class ValList(list):
    """A list of Val objects."""

    def __init__(self, *vals: Val) -> None:
        """Initialize a ValList.

        Args:
            *vals (Val): Variable number of Val objects.

        Raises:
            TypeError: If any item is not a Val instance.
        """
        for v in vals:
            if not isinstance(v, Val):
                raise TypeError(
                    f"Items in ValList must be Val instances, got {type(v)}"
                )
        super().__init__(vals)

    def append(self, item: Val) -> None:
        """Append a Val to the list.

        Args:
            item (Val): The Val to append.

        Raises:
            TypeError: If item is not a Val instance.
        """
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only append Val instances to ValList, got {type(item)}"
            )
        super().append(item)

    def extend(self, iterable: list[Val]) -> None:
        """Extend the list with Val objects from an iterable.

        Args:
            iterable (Iterable[Val]): Iterable of Val objects.

        Raises:
            TypeError: If any item is not a Val instance.
        """
        for item in iterable:
            if not isinstance(item, Val):
                raise TypeError(
                    f"Items in ValList must be Val instances, got {type(item)}"
                )
        super().extend(iterable)

    def insert(self, index: int, item: Val) -> None:
        """Insert a Val at a given position.

        Args:
            index (int): Position to insert.
            item (Val): The Val to insert.

        Raises:
            TypeError: If item is not a Val instance.
        """
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only insert Val instances to ValList, got {type(item)}"
            )
        super().insert(index, item)

    def __repr__(self) -> str:
        """Return a string representation of the ValList.

        Returns:
            str: String representation.
        """
        return f"ValSet({', '.join(repr(val) for val in self)})"

    def unpack(self) -> ValList:
        """Unpack all Val objects in the set.

        Returns:
            ValList: A new ValList with all unpacked Val objects.
        """
        vals = []
        for val in self:
            vals.extend(val.unpack())
        return ValList(*vals)
