"""varmeta: Lightweight variable metadata management for data workflows.

This package provides hashable variable objects with units, descriptions, and
component support, enabling robust metadata handling, serialization, and
integration with pandas and other tools.
"""

from .vals import Val, ValList
from .vars import Var, VarData, to_df, vars_to_multi_index_data

__version__ = "0.0.1"

__all__ = [
    "Var",
    "Val",
    "ValList",
    "vars_to_multi_index_data",
    "to_df",
    "VarData",
]
