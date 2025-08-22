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
            "component_axis": self.component_axis
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