"""Core classes and functions for varmeta."""

from __future__ import annotations

from .vars import Var
from typing import Callable


class Val:
    def __init__(
        self, value: object, var: Var, unpack_func: Callable | None = None
    ):
        self.value = value
        self.var = var
        self.unpack_func = unpack_func

    def __repr__(self) -> str:
        return f"Val(value={self.value!r}, var={self.var})"

    def unpack(self) -> list[Val]:
        """Unpack the value components into a list of Val items."""
        unpackable_vars, unpackable_vals = self.var.unpack(self.value)
        return [
            Val(value=val, var=var)
            for val, var in zip(unpackable_vals, unpackable_vars, strict=True)
        ]


class ValList(list):
    """A list of Val objects."""

    def __init__(self, *vals: Val):
        for v in vals:
            if not isinstance(v, Val):
                raise TypeError(
                    f"All items in ValList must be Val instances, got {type(v)}"
                )
        super().__init__(vals)

    def append(self, item):
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only append Val instances to ValList, got {type(item)}"
            )
        super().append(item)

    def extend(self, iterable):
        for item in iterable:
            if not isinstance(item, Val):
                raise TypeError(
                    f"All items in ValList must be Val instances, got {type(item)}"
                )
        super().extend(iterable)

    def insert(self, index, item):
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only insert Val instances to ValList, got {type(item)}"
            )
        super().insert(index, item)

    def __repr__(self) -> str:
        return f"ValSet({', '.join(repr(val) for val in self)})"

    def unpack(self) -> ValList:
        """Unpack all Val objects in the set."""
        vals = []
        for val in self:
            vals.extend(val.unpack())
        return ValList(*vals)


class ValDict(dict):
    """A dict of Var: value pairs. Keys must be Var instances."""
    _key_index: dict[str, Var]

    def __init__(self, *args, **kwargs):
        self._key_index = {}
        super().__init__()
        if len(args) > 0:
            if len(args) > 1:
                raise TypeError(
                    f"ValDict expected at most 1 argument, got {len(args)}"
                )
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():
                    self[k] = v
            else:
                for k, v in other:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v  # type: ignore

    def __setitem__(self, key: Var, value: object):
        if not isinstance(key, Var):
            raise TypeError(
                f"ValDict keys must be Var instances, got {type(key)}"
            )
        super().__setitem__(key, value)
        if key.key in self._key_index and self._key_index[key.key] != key:
            raise KeyError(
                f"Key conflict: '{key.key}' already exists in ValDict"
            )
        self._key_index[key.key] = key

    def update(self, *args, **kwargs):
        if len(args) > 0:
            if len(args) > 1:
                raise TypeError(
                    f"update expected at most 1 argument, got {len(args)}"
                )
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():
                    self[k] = v
            else:
                for k, v in other:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v  # type: ignore

    def unpack(self) -> "ValDict":
        """Unpack all Val objects in the set."""
        vals = {}
        for var, value in self.items():
            unpackable_vars, unpackable_vals = var.unpack(value)
            for val, var in zip(unpackable_vals, unpackable_vars, strict=True):
                vals[var] = val
        return ValDict(vals)

    def find_var(self, key: str) -> Var:
        """Get a Var by its key."""
        return self._key_index[key]

    def find(self, key: str) -> object:
        """Get a value by its key."""
        return self[self._key_index.get(key)]
