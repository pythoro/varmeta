"""Naming rules for matching flat table columns to Vars."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from .vars import Var


@dataclass(frozen=True)
class ColumnNaming:
    """How a flat table names the columns of a VarSet's Vars.

    Args:
        separator: Text between a Var key and a component name.
            Defaults to ``"__"``, varmeta's own convention.
        prefixes: Group prefixes to strip from a column stem, tried
            in the order listed (e.g. ``("loads_",)``).
        derived: Component suffixes valid for any Var that has
            components (e.g. ``("mag",)``).

    Raises:
        ValueError: If separator is empty.
    """

    separator: str = "__"
    prefixes: tuple[str, ...] = ()
    derived: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate the naming rule.

        Raises:
            ValueError: If separator is empty.
        """
        if not self.separator:
            raise ValueError("ColumnNaming.separator must not be empty.")


class ColumnMatch(NamedTuple):
    """The Var that a flat column name refers to.

    Attributes:
        column: The column name as given.
        var: The parent Var (not a component Var).
        component: The component suffix (e.g. ``"x"`` or ``"mag"``),
            or None for a whole-Var column.
        stem: The column without its component suffix, with any
            prefix kept (e.g. ``"loads_force"`` for
            ``"loads_force_x"``).
    """

    column: str
    var: Var
    component: str | None
    stem: str
