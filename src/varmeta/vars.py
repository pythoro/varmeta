"""Core classes and functions for varmeta."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

import numpy as np


class VarData(TypedDict):
    """TypedDict for Var data serialization."""

    key: str
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    component_axis: int


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
        }

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
            )
            for comp in self.components
        ]

    def unpack(self, data: object) -> dict[Var, object]:
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
            packed_vals = data_array
        elif self.component_axis > data_array.ndim - 1:
            raise ValueError(
                f"Component axis {self.component_axis} is out of bounds for"
                + " data with {data_array.ndim} dimensions."
            )
        else:
            packed_vals = np.moveaxis(data_array, self.component_axis, 0)  # type: ignore
        if not isinstance(data, np.ndarray):
            packed_vals = packed_vals.tolist()
        packed_vars = self.component_vars()
        unpacked_dict = {}
        for val, var in zip(packed_vals, packed_vars, strict=True):
            unpacked_dict[var] = val
        return unpacked_dict


class Store:
    """A store for Var objects."""

    vars: dict[str, Var]

    def __init__(self) -> None:
        """Initialize the Store."""
        self.vars = {}

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
