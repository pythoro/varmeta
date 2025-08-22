"""varmeta: Lightweight variable metadata management for data workflows.

This package provides hashable variable objects with units, descriptions, and
component support, enabling robust metadata handling, serialization, and
integration with pandas and other tools.
"""

from .vals import Val, ValDict, ValList
from .vars import Var

__version__ = "0.0.1"

__all__ = ["Var", "Val", "ValList", "ValDict"]
