"""Core classes and functions for varmeta."""

from __future__ import annotations

from .vars import Store, Var


class Val:
    """A value associated with a Var object.

    Attributes:
        data (object): The value data.
        var (Var): The associated Var instance.
    """

    def __init__(self, data: object, var: Var) -> None:
        """Initialize a Val instance.

        Args:
            data (object): The value data.
            var (Var): The associated Var instance.
        """
        self.data = data
        self.var = var

    def __repr__(self) -> str:
        """Return a string representation of the Val.

        Returns:
            str: String representation.
        """
        return f"Val(data={self.data!r}, var={self.var})"

    def unpack(self) -> list[Val]:
        """Unpack the data components into a list of Val items.

        Returns:
            list[Val]: List of unpacked Val objects.
        """
        dct = self.var.unpack(self.data)
        return [Val(data, var) for var, data in dct.items()]


class ValList(list):
    """A list of Val objects."""

    def __init__(self, *vals: Val) -> None:
        """Initialize a ValList.

        Args:
            *vals (Val): Variable number of Val objects.

        Raises:
            TypeError: If any item is not a Val instance.
        """
        for v in vals:
            if not isinstance(v, Val):
                raise TypeError(
                    f"Items in ValList must be Val instances, got {type(v)}"
                )
        super().__init__(vals)

    def append(self, item: Val) -> None:
        """Append a Val to the list.

        Args:
            item (Val): The Val to append.

        Raises:
            TypeError: If item is not a Val instance.
        """
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only append Val instances to ValList, got {type(item)}"
            )
        super().append(item)

    def extend(self, iterable: list[Val]) -> None:
        """Extend the list with Val objects from an iterable.

        Args:
            iterable (Iterable[Val]): Iterable of Val objects.

        Raises:
            TypeError: If any item is not a Val instance.
        """
        for item in iterable:
            if not isinstance(item, Val):
                raise TypeError(
                    f"Items in ValList must be Val instances, got {type(item)}"
                )
        super().extend(iterable)

    def insert(self, index: int, item: Val) -> None:
        """Insert a Val at a given position.

        Args:
            index (int): Position to insert.
            item (Val): The Val to insert.

        Raises:
            TypeError: If item is not a Val instance.
        """
        if not isinstance(item, Val):
            raise TypeError(
                f"Can only insert Val instances to ValList, got {type(item)}"
            )
        super().insert(index, item)

    def __repr__(self) -> str:
        """Return a string representation of the ValList.

        Returns:
            str: String representation.
        """
        return f"ValSet({', '.join(repr(val) for val in self)})"

    def unpack(self) -> ValList:
        """Unpack all Val objects in the set.

        Returns:
            ValList: A new ValList with all unpacked Val objects.
        """
        vals = []
        for val in self:
            vals.extend(val.unpack())
        return ValList(*vals)


class ValDict(dict):
    """A dict of Var: data pairs. Keys must be Var instances."""

    _store: Store

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize a ValDict.

        Args:
            *args: Positional arguments for dict initialization.
            **kwargs: Keyword arguments for dict initialization.

        Raises:
            TypeError: If keys are not Var instances.
        """
        self._store = Store()
        super().__init__()
        if len(args) > 0:
            if len(args) > 1:
                raise TypeError(
                    f"ValDict expected at most 1 argument, got {len(args)}"
                )
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():  # type: ignore
                    self[k] = v
            else:
                for k, v in other:  # type: ignore
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v  # type: ignore

    @classmethod
    def from_dicts(
        cls, data_dict: dict[str, object], var_data: dict[str, dict]
    ) -> ValDict:
        """Create a ValDict from data and variable metadata dicts.

        Args:
            data_dict (dict[str, object]): Mapping from var key to value.
            var_data (dict[str, dict]): Mapping from var key to var
                metadata dict.

        Returns:
            ValDict: Constructed ValDict instance.
        """
        var_dct = {key: Var(**data) for key, data in var_data.items()}
        dct = {var_dct[key]: data for key, data in data_dict.items()}
        return cls(dct)

    def __setitem__(self, var: Var, data: object) -> None:
        """Set a value in the ValDict.

        Args:
            var (Var): The Var key.
            data (object): The value to set.

        Raises:
            TypeError: If key is not a Var instance.
        """
        if not isinstance(var, Var):
            raise TypeError(
                f"ValDict keys must be Var instances, got {type(var)}"
            )
        super().__setitem__(var, data)
        self._store.add(var)

    def update(self, *args: object, **kwargs: object) -> None:
        """Update the ValDict with new values.

        Args:
            *args: Positional arguments for dict update.
            **kwargs: Keyword arguments for dict update.

        Raises:
            TypeError: If keys are not Var instances.
        """
        if len(args) > 0:
            if len(args) > 1:
                raise TypeError(
                    f"update expected at most 1 argument, got {len(args)}"
                )
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():  # type: ignore
                    self[k] = v
            else:
                for k, v in other:  # type: ignore
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v  # type: ignore

    def unpack(self) -> ValDict:
        """Unpack all Val objects in the set.

        Returns:
            ValDict: A new ValDict with unpacked values.
        """
        vals = {}
        for var, data in self.items():
            subdict = var.unpack(data)
            vals.update(subdict)  # type: ignore
        return ValDict(vals)

    def find_var(self, key: str) -> Var:
        """Get a Var by its key.

        Args:
            key (str): The key of the Var.

        Returns:
            Var: The Var instance.
        """
        return self._store.get(key)

    def find(self, key: str) -> object:
        """Get a data by its key.

        Args:
            key (str): The key of the Var.

        Returns:
            object: The value associated with the Var.
        """
        return self[self._store.get(key)]

    def to_dict(self) -> dict:
        """Convert the ValDict to a regular dict.

        Returns:
            dict: Dictionary mapping Var keys to values.
        """
        return {var.key: data for var, data in self.items()}

    def var_data(self) -> dict:
        """Return a dictionary of Var object data.

        Returns:
            dict: Dictionary mapping Var keys to Var metadata dicts.
        """
        return self._store.to_dict()
