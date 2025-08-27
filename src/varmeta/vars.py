"""Core classes and functions for varmeta."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NotRequired, TypedDict

import numpy as np
from numpy.typing import NDArray

try:
    import pandas as pd
except ImportError:
    pd = None


class VarData(TypedDict):
    """TypedDict for Var data serialization."""

    key: str
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    component_axis: int
    data_type: NotRequired[str | None]


@dataclass(frozen=True, order=True)
class Var:
    """A variable with metadata.

    Attributes:
        key (str): Unique identifier for the variable.
        name (str): Human-readable name.
        units (str): Units of measurement.
        desciption (str): Description of the variable.
        components (tuple[str, ...] | None): Tuple of component names, or None.
        component_axis (int): Axis along which to unpack components.
    """

    key: str = field(compare=False)
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    component_axis: int = 0
    data_type: str | None = "object"

    def __str__(self) -> str:
        """Return a string representation of the variable.

        Returns:
            str: The variable name and units.
        """
        desc = f"{self.name} [{self.units}]"
        return desc

    def __repr__(self) -> str:
        """Return a string representation of the variable.

        Returns:
            str: The variable name and units.
        """
        desc = f"{self.name} [{self.units}]"
        return desc

    def to_dict(self) -> VarData:
        """Convert the Var to a dictionary.

        Returns:
            VarData: Dictionary representation of the Var.
        """
        return {
            "key": self.key,
            "name": self.name,
            "units": self.units,
            "desciption": self.desciption,
            "components": self.components,
            "component_axis": self.component_axis,
            "data_type": self.data_type,
        }

    def validate(self, data: object, raise_type_error: bool = True) -> bool:
        """Validate that the data matches the Var's data_type.

        Args:
            data (object): The data to validate.
            raise_type_error (bool): If True, raise TypeError on mismatch.

        Returns:
            bool: True if data matches the Var's data_type, False otherwise.
        """
        if self.data_type is None or self.data_type == "object":
            return True
        if type(data).__name__ != self.data_type:
            if raise_type_error:
                raise TypeError(f"Expected {self.data_type}, got {type(data)}")
            return False
        return True

    def component_vars(self) -> list[Var]:
        """Return a list of component variables.

        Returns:
            list[Var]: List of component Var objects.
        """
        if self.components is None:
            return []
        return [
            Var(
                key=f"{self.key}_{comp}",
                name=f"{self.name} {comp}",
                units=self.units,
                desciption=self.desciption,
                components=None,
                data_type=self.data_type,
            )
            for comp in self.components
        ]

    def unpack(self, data: object) -> tuple[list[Var], list[object] | NDArray]:
        """Unpack the value into component variables.

        Args:
            data (Any): The data to unpack (should be array-like).

        Returns:
            tuple[list[Var], list[Any]]: Tuple of component Vars and
            unpacked values.

        Raises:
            ValueError: If no components to unpack or data is not iterable.
        """
        if self.components is None:
            raise ValueError("No components to unpack")
        if isinstance(data, float | int):
            raise ValueError("Values must be iterable")
        data_array = np.asarray(data)
        if data_array.ndim < 1:
            raise ValueError("Data must be at least 1-dimensional to unpack.")
        if data_array.ndim == 1:
            # Ignore the axis as there's only one dimension
            subvals = data_array
        elif self.component_axis > data_array.ndim - 1:
            raise ValueError(
                f"Component axis {self.component_axis} is out of bounds for"
                + " data with {data_array.ndim} dimensions."
            )
        else:
            subvals = np.moveaxis(data_array, self.component_axis, 0)  # type: ignore
        if not isinstance(data, np.ndarray):
            subvals = subvals.tolist()
        subvars = self.component_vars()
        return subvars, subvals

    def unpack_tuples(self, data: object) -> list[tuple[Var, object]]:
        """Unpack the value into component variables.

        Args:
            data (Any): The data to unpack (should be array-like).

        Returns:
            list[tuple[Var, object]]: List of tuples of component Var and
            unpacked value.

        Raises:
            ValueError: If no components to unpack or data is not iterable.
        """
        packed_vars, packed_vals = self.unpack(data)
        tuples = list(zip(packed_vars, packed_vals, strict=True))
        return tuples


def unpack(
    var_dct: dict[str, Var], data_dct: dict[str, Any]
) -> tuple[dict[str, Var], dict[str, Any]]:
    """Get var components for all the vars.

    Returns:
        tuple[dict[str, Var], dict[str, object]]: Tuple of two dicts:
            - Mapping from var key to Var object (including components).
            - Mapping from var key to unpacked data values.
    """
    vars = {}
    vals = {}
    for key, data in data_dct.items():
        var = var_dct[key]
        subvars = var.component_vars()
        if subvars:
            tuples = var.unpack_tuples(data)
            for subvar, subval in tuples:
                vals[subvar.key] = subval
                vars[subvar.key] = subvar
        else:
            vals[key] = data
            vars[key] = var
    return vars, vals


def vars_to_multi_index_data(
    lst: list[Var],
    attrs: list[str] | None = None,
) -> tuple[list[tuple[str, str]], list[str]]:
    """Convert a list of Vars to MultiIndex data.

    Args:
        lst: List of Var objects.
        attrs: List of Var attributes to use for MultiIndex levels.

    Returns:
        tuple[list[str], list[str]]: Tuple of two lists:
            - List of variable names.
            - List of variable units.
    """
    tuples = []
    attrs = ["key", "name", "units"] if attrs is None else attrs
    for var in lst:
        tuples.append(tuple([getattr(var, attr) for attr in attrs]))
    return tuples, attrs


def to_df(
    var_dct: dict[str, Var],
    data_dct: dict[str, Any],
    attrs: list[str] | None = None,
) -> pd.DataFrame:
    """Convert a dict of Vars and data to a pandas DataFrame.

    Args:
        var_dct: Dictionary mapping var keys to Var objects.
        data_dct: Dictionary mapping var keys to data values.
        attrs: List of Var attributes to use for MultiIndex levels.

    Returns:
        pd.DataFrame: DataFrame with MultiIndex columns based on Var metadata.
    """
    var_dct, data_dct = unpack(var_dct, data_dct)
    var_list = [var_dct[key] for key in data_dct]
    tuples, names = vars_to_multi_index_data(var_list, attrs=attrs)
    columns = pd.MultiIndex.from_tuples(tuples, names=names)
    df = pd.DataFrame(data_dct)
    df.columns = columns
    return df
