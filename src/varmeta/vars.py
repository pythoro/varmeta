"""Core classes and functions for varmeta."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True, order=True)
class Var:
    key: str = field(compare=False)
    name: str
    units: str
    desciption: str
    components: tuple[str, ...] | None
    unpack_func: Callable | None = None

    def __str__(self) -> str:
        desc = f"{self.name} [{self.units}]"
        return desc

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
                unpack_func=self.unpack_func,
            )
            for comp in self.components
        ]
    

    def unpack(self, value):
        """Unpack the value into component variables."""
        if self.components is None:
            raise ValueError("No components to unpack")
        if isinstance(value, (float, int)):
            raise ValueError("Values must be iterable")
        if self.unpack_func is None:
            unpackable_vals = value
        else:
            unpackable_vals = self.unpack_func(value)
        return self.component_vars(), unpackable_vals