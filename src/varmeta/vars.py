"""Core classes and functions for varmeta."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NotRequired, TypedDict

import numpy as np
from numpy.typing import NDArray


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


class Store:
    """A store for Var objects."""

    vars: dict[str, Var]

    def __init__(self) -> None:
        """Initialize the Store."""
        self.vars = {}

    @classmethod
    def from_dict(cls, var_data: dict[str, VarData]) -> Store:
        """Create a Store from a dictionary of Var data.

        Args:
            var_data (dict[str, dict]): Mapping from var key to var
                metadata dict.

        Returns:
            Store: Constructed Store instance.
        """
        store = cls()
        for key, data in var_data.items():
            if data["key"] != key:
                raise ValueError(
                    f"Key mismatch: dict key '{key}' does not match "
                    + f"VarData key '{data['key']}'"
                )
            var = Var(**data)
            store.add(var)
        return store

    def add(self, var: Var) -> None:
        """Add a Var to the store.

        Args:
            var (Var): The Var to add.

        Raises:
            TypeError: If var is not a Var instance.
            KeyError: If a different Var with the same key already exists.
        """
        if not isinstance(var, Var):
            raise TypeError("Only Var instances can be added")
        if var.key in self.vars and self.vars[var.key] != var:
            raise KeyError(
                f"Duplicate key detected. \nExisting:\n{self.vars[var.key]}\n"
                + f"New:\n{var.key}"
            )
        self.vars[var.key] = var
        # Also add component vars if they exist
        if var.components is not None:
            for comp_var in var.component_vars():
                if (
                    comp_var.key in self.vars
                    and self.vars[comp_var.key] != comp_var
                ):
                    raise KeyError(
                        "Duplicate key detected. \nExisting:\n"
                        + f"{self.vars[comp_var.key]}\nNew:\n{comp_var}"
                    )
                self.vars[comp_var.key] = comp_var

    def get(self, key: str) -> Var:
        """Get a Var by its key.

        Args:
            key (str): The key of the Var.

        Returns:
            Var: The Var with the given key.
        """
        return self.vars[key]

    def remove(self, key: str) -> None:
        """Remove a Var by its key.

        Args:
            key (str): The key of the Var to remove.

        Raises:
            KeyError: If the key is not found.
        """
        if key in self.vars:
            del self.vars[key]
        else:
            raise KeyError(f"Var with key '{key}' not found")

    def to_list(self) -> list[Var]:
        """Return all stored Vars as a list.

        Returns:
            list[Var]: List of all Vars in the store.
        """
        return list(self.vars.values())

    def to_dict(self) -> dict[str, VarData]:
        """Return a dictionary of Var object data.

        Returns:
            dict[str, VarData]: Dictionary mapping keys to Var data dicts.
        """
        return {var.key: var.to_dict() for var in self.vars.values()}

    def unpack(
        self, dct: dict[str, object]
    ) -> tuple[dict[str, Var], dict[str, object]]:
        """Get var components for all the vars.

        Returns:
            tuple[dict[str, Var], dict[str, object]]: Tuple of two dicts:
                - Mapping from var key to Var object (including components).
                - Mapping from var key to unpacked data values.
        """
        vars = {}
        vals = {}
        for key, data in dct.items():
            var = self.vars[key]
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
