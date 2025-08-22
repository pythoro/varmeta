"""Core classes and functions for varmeta."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import numpy as np

from typing import TypedDict


class VarData(TypedDict):
    key: str
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    component_axis: int


@dataclass(frozen=True, order=True)
class Var:
    """A variable with metadata."""

    key: str = field(compare=False)
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    component_axis: int = 0

    def __str__(self) -> str:
        desc = f"{self.name} [{self.units}]"
        return desc

    def to_dict(self) -> VarData:
        """Convert the Var to a dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "units": self.units,
            "desciption": self.desciption,
            "components": self.components,
            "component_axis": self.component_axis,
        }

    def component_vars(self) -> list[Var]:
        """Return a list of component variables."""
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

    def unpack(self, data):
        """Unpack the value into component variables."""
        if self.components is None:
            raise ValueError("No components to unpack")
        if isinstance(data, (float, int)):
            raise ValueError("Values must be iterable")
        packed_vals = np.moveaxis(data, self.component_axis, 0)
        if not isinstance(data, np.ndarray):
            packed_vals = packed_vals.tolist()
        packed_vars = self.component_vars()
        return packed_vars, packed_vals


class Store:
    """A store for Var objects."""

    def __init__(self):
        self.vars = {}

    def add(self, var: Var):
        """Add a Var to the store."""
        if not isinstance(var, Var):
            raise TypeError("Only Var instances can be added")
        if var.key in self.vars and self.vars[var.key] != var:
            raise KeyError(
                f"Duplicate key detected. \nExisting:\n{self.vars[var.key]}\n"
                + f"New:\n{var.key}"
            )
        self.vars[var.key] = var

    def get(self, key: str) -> Var:
        """Get a Var by its key."""
        return self.vars[key]

    def remove(self, key: str):
        """Remove a Var by its key."""
        if key in self.vars:
            del self.vars[key]
        else:
            raise KeyError(f"Var with key '{key}' not found")

    def to_list(self) -> list[Var]:
        """Return all stored Vars as a list."""
        return list(self.vars.values())

    def to_dict(self) -> dict:
        """Return a dictionary of Var object data."""
        return {var.key: var.to_dict() for var in self.vars.values()}
