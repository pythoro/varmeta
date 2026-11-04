"""varmeta: Lightweight variable metadata management for data workflows.

This package provides hashable variable objects with units, descriptions, and
component support, enabling robust metadata handling, serialization, and
integration with pandas and other tools.
"""

from .columns import ColumnMatch, ColumnNaming
from .vars import Var, VarData
from .varset import VarSet

__all__ = [
    "ColumnMatch",
    "ColumnNaming",
    "Var",
    "VarData",
    "VarSet",
]
