"""Core classes and functions for varmeta."""

from __future__ import annotations

from collections.abc import Callable

from .vars import Var, Store


class Val:
    def __init__(
        self, data: object, var: Var
    ):
        self.data = data
        self.var = var

    def __repr__(self) -> str:
        return f"Val(data={self.data!r}, var={self.var})"

    def unpack(self) -> list[Val]:
        """Unpack the data components into a list of Val items."""
        unpackable_vars, unpackable_vals = self.var.unpack(self.data)
        return [
            Val(data=val, var=var)
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
    """A dict of Var: data pairs. Keys must be Var instances."""

    _store: Store

    def __init__(self, *args, **kwargs):
        self._store = Store()
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

    @classmethod
    def from_dicts(
        cls, data_dict: dict[str, object], var_data: dict[str, dict]
    ) -> ValDict:
        var_dct = {key: Var(**data) for key, data in var_data.items()}
        dct = {var_dct[key]: data for key, data in data_dict.items()}
        return cls(dct)

    def __setitem__(self, var: Var, data: object):
        if not isinstance(var, Var):
            raise TypeError(
                f"ValDict keys must be Var instances, got {type(var)}"
            )
        super().__setitem__(var, data)
        self._store.add(var)

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

    def unpack(self) -> ValDict:
        """Unpack all Val objects in the set."""
        vals = {}
        for var, data in self.items():
            unpackable_vars, unpackable_vals = var.unpack(data)
            for val, var in zip(unpackable_vals, unpackable_vars, strict=True):
                vals[var] = val
        return ValDict(vals)

    def find_var(self, key: str) -> Var:
        """Get a Var by its key."""
        return self._store.get(key)

    def find(self, key: str) -> object:
        """Get a data by its key."""
        return self[self._store.get(key)]

    def to_dict(self) -> dict:
        """Convert the ValDict to a regular dict."""
        return {var.key: data for var, data in self.items()}

    def var_data(self) -> dict:
        """Return a dictionary of Var object data."""
        return self._store.to_dict()
