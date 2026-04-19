"""varmeta: Lightweight variable metadata management for data workflows.

This package provides hashable variable objects with units, descriptions, and
component support, enabling robust metadata handling, serialization, and
integration with pandas and other tools.
"""

from .vars import Var, VarData
from .varset import VarSet

__all__ = [
    "Var",
    "VarData",
    "VarSet",
]
