"""VarSet: a collection of Var instances for data workflows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, overload

import pandas as pd

from .vars import Var, VarData, _unpack, _vars_to_multi_index_data


class VarSet:
    """An ordered collection of Var instances.

    Provides dict-like access by key, component unpacking,
    DataFrame construction, and serialization.

    Args:
        vars: A sequence of Var instances or a dict mapping
            string keys to Var instances.

    Raises:
        TypeError: If vars is not a Sequence or dict.

    Examples:
        >>> varset = VarSet([temperature, force])
        >>> varset = VarSet({"temp": temperature, "force": force})
    """

    def __init__(
        self,
        vars: Sequence[Var] | dict[str, Var],
    ) -> None:
        """Initialize a VarSet.

        Args:
            vars: A sequence of Var instances or a dict
                mapping string keys to Var instances.
        """
        if isinstance(vars, dict):
            self._vars: dict[str, Var] = dict(vars)
        elif isinstance(vars, Sequence):
            self._vars = {v.key: v for v in vars}
        else:
            raise TypeError(
                f"Expected Sequence[Var] or dict[str, Var],"
                f" got {type(vars)}"
            )

    def __getitem__(self, key: str) -> Var:
        """Get a Var by its string key.

        Args:
            key: The string key of the variable.

        Returns:
            Var: The variable with the given key.
        """
        return self._vars[key]

    def __contains__(self, key: object) -> bool:
        """Check if a key exists in the VarSet.

        Args:
            key: The string key to check.

        Returns:
            bool: True if the key exists.
        """
        return key in self._vars

    def __iter__(self):  # noqa: ANN204
        """Iterate over the string keys.

        Returns:
            Iterator[str]: Iterator over keys.
        """
        return iter(self._vars)

    def __len__(self) -> int:
        """Return the number of variables.

        Returns:
            int: Number of variables.
        """
        return len(self._vars)

    def __repr__(self) -> str:
        """Return a string representation.

        Returns:
            str: String representation of the VarSet.
        """
        return repr(self._vars)

    def keys(self) -> dict[str, Var].keys:  # type: ignore[type-arg]
        """Return the string keys.

        Returns:
            dict_keys: The keys of the VarSet.
        """
        return self._vars.keys()

    def values(self) -> dict[str, Var].values:  # type: ignore[type-arg]
        """Return the Var values.

        Returns:
            dict_values: The Var instances.
        """
        return self._vars.values()

    def items(self) -> dict[str, Var].items:  # type: ignore[type-arg]
        """Return key-Var pairs.

        Returns:
            dict_items: The key-Var pairs.
        """
        return self._vars.items()

    def unpack(
        self, data: dict[str, Any],
    ) -> tuple[VarSet, dict[str, Any]]:
        """Expand component variables in the data.

        Args:
            data: Dictionary mapping var keys to data values.

        Returns:
            tuple[VarSet, dict[str, Any]]: A new VarSet with
                component variables expanded, and the
                corresponding unpacked data dict.
        """
        new_vars, new_data = _unpack(self._vars, data)
        return VarSet(new_vars), new_data

    @overload
    def to_dataframe(
        self,
        data: dict[str, Any],
        attrs: list[str] | None = ...,
    ) -> pd.DataFrame: ...

    @overload
    def to_dataframe(
        self,
        data: list[dict[str, Any]],
        attrs: list[str] | None = ...,
    ) -> pd.DataFrame: ...

    def to_dataframe(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
        attrs: list[str] | None = None,
    ) -> pd.DataFrame:
        """Build a pandas DataFrame with MultiIndex columns.

        Automatically unpacks component variables. Accepts a
        single data dict (one row per value) or a list of dicts
        (one row per dict).

        Args:
            data: A single data dict or list of data dicts.
            attrs: Var attributes for MultiIndex levels.
                Defaults to ``["key", "name", "units"]``.

        Returns:
            pd.DataFrame: DataFrame with MultiIndex columns.
        """
        if isinstance(data, list):
            return self._records_to_df(data, attrs)
        return self._dict_to_df(data, attrs)

    def _dict_to_df(
        self,
        data: dict[str, Any],
        attrs: list[str] | None = None,
    ) -> pd.DataFrame:
        """Build DataFrame from a single data dict.

        Args:
            data: Dictionary mapping var keys to data values.
            attrs: Var attributes for MultiIndex levels.

        Returns:
            pd.DataFrame: DataFrame with MultiIndex columns.
        """
        unpacked_vars, unpacked_data = _unpack(
            self._vars, data,
        )
        var_list = [
            unpacked_vars[key] for key in unpacked_data
        ]
        tuples, names = _vars_to_multi_index_data(
            var_list, attrs=attrs,
        )
        columns = pd.MultiIndex.from_tuples(
            tuples, names=names,
        )
        
        # Check if all unpacked values are scalars
        # (happens when components are unpacked from a single vector)
        import numpy as np
        all_scalars = all(
            not isinstance(val, list | tuple | np.ndarray)
            for val in unpacked_data.values()
        )
        if all_scalars:
            # Wrap scalars in lists to create single-row DataFrame
            unpacked_data = {
                key: [val] for key, val in unpacked_data.items()
            }
        
        df = pd.DataFrame(unpacked_data)
        df.columns = columns
        return df

    def _records_to_df(
        self,
        data_list: list[dict[str, Any]],
        attrs: list[str] | None = None,
    ) -> pd.DataFrame:
        """Build DataFrame from a list of data dicts.

        Args:
            data_list: List of data dicts.
            attrs: Var attributes for MultiIndex levels.

        Returns:
            pd.DataFrame: DataFrame with MultiIndex columns.

        Raises:
            ValueError: If the data list is empty.
        """
        var_list = None
        unpacked = []
        for record in data_list:
            unpacked_vars, unpacked_data = _unpack(
                self._vars, record,
            )
            if var_list is None:
                var_list = [
                    unpacked_vars[key]
                    for key in unpacked_data
                ]
            unpacked.append(unpacked_data)
        if var_list is None:
            raise ValueError(
                "No data or malformed data provided."
            )
        tuples, names = _vars_to_multi_index_data(
            var_list, attrs=attrs,
        )
        columns = pd.MultiIndex.from_tuples(
            tuples, names=names,
        )
        df = pd.DataFrame.from_records(unpacked)
        df.columns = columns
        return df

    def to_dict(self) -> dict[str, VarData]:
        """Serialize to a JSON-compatible dictionary.

        Returns:
            dict[str, VarData]: Dictionary mapping keys to
                VarData representations.
        """
        return {
            key: var.to_dict()
            for key, var in self._vars.items()
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, VarData],
    ) -> VarSet:
        """Deserialize from a dictionary of VarData.

        Args:
            data: Dictionary mapping keys to VarData dicts.

        Returns:
            VarSet: A new VarSet instance.
        """
        return cls({
            key: Var.from_dict(var_data)
            for key, var_data in data.items()
        })
