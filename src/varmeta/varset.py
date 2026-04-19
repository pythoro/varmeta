"""VarSet: a collection of Var instances for data workflows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, overload

import numpy as np
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

    def _validate_dict_vars(self, vars: dict[str, Var]) -> None:
        """Validate dict of Vars.

        Args:
            vars: Dict mapping keys to Var instances.

        Raises:
            ValueError: If dict is empty.
            TypeError: If any value is not a Var.
        """
        if not vars:
            raise ValueError(
                "Cannot create VarSet from empty dict. "
                "Provide at least one Var instance."
            )
        for key, var in vars.items():
            if not isinstance(var, Var):
                raise TypeError(
                    f"Dict values must be Var instances. "
                    f"Key '{key}' has value of type "
                    f"{type(var).__name__}."
                )

    def _sequence_to_dict(
        self, vars: Sequence[Var],
    ) -> dict[str, Var]:
        """Convert sequence of Vars to dict.

        Args:
            vars: Sequence of Var instances.

        Returns:
            dict[str, Var]: Dict mapping keys to Vars.

        Raises:
            ValueError: If sequence is empty or has duplicates.
            TypeError: If any item is not a Var.
        """
        if not vars:
            raise ValueError(
                "Cannot create VarSet from empty sequence. "
                "Provide at least one Var instance."
            )
        for i, var in enumerate(vars):
            if not isinstance(var, Var):
                raise TypeError(
                    f"Sequence items must be Var instances. "
                    f"Item at index {i} has type "
                    f"{type(var).__name__}."
                )
        result = {}
        for var in vars:
            if var.key in result:
                raise ValueError(
                    f"Duplicate key '{var.key}' found in Var "
                    f"sequence. All Var keys must be unique."
                )
            result[var.key] = var
        return result

    def __init__(
        self,
        vars: Sequence[Var] | dict[str, Var],
    ) -> None:
        """Initialize a VarSet.

        Args:
            vars: A sequence of Var instances or a dict
                mapping string keys to Var instances.

        Raises:
            TypeError: If vars is not a Sequence or dict, or
                contains non-Var items.
            ValueError: If vars is empty or contains duplicate keys.
        """
        if isinstance(vars, dict):
            self._validate_dict_vars(vars)
            self._vars: dict[str, Var] = dict(vars)
        elif isinstance(vars, Sequence):
            self._vars = self._sequence_to_dict(vars)
        else:
            raise TypeError(
                f"Expected Sequence[Var] or dict[str, Var], "
                f"got {type(vars).__name__}."
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
        self, data: dict[str, Any], raise_extra: bool = False,
    ) -> tuple[VarSet, dict[str, Any]]:
        """Expand component variables in the data.

        Args:
            data: Dictionary mapping var keys to data values.
            raise_extra: If True, raise KeyError for extra keys in data.
                If False, silently ignore extra keys. Defaults to False.

        Returns:
            tuple[VarSet, dict[str, Any]]: A new VarSet with
                component variables expanded, and the
                corresponding unpacked data dict.

        Raises:
            TypeError: If data is not a dict.
            KeyError: If data keys don't match VarSet keys.
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"Data must be a dict, got {type(data).__name__}."
            )
        # Check for missing and extra keys
        data_keys = set(data.keys())
        var_keys = set(self._vars.keys())
        missing = var_keys - data_keys
        extra = data_keys - var_keys
        
        # Check for errors
        if missing or (extra and raise_extra):
            msg_parts = []
            if missing:
                msg_parts.append(
                    f"Missing keys in data: {sorted(missing)}"
                )
            if extra and raise_extra:
                msg_parts.append(
                    f"Extra keys in data: {sorted(extra)}"
                )
            msg = ". ".join(msg_parts)
            msg += f". Expected keys: {sorted(var_keys)}."
            raise KeyError(msg)
        
        # Filter out extra keys before unpacking (if we didn't raise above)
        if extra and not raise_extra:
            data = {k: v for k, v in data.items() if k in var_keys}
        
        new_vars, new_data = _unpack(self._vars, data)
        return VarSet(new_vars), new_data

    def _pack_component_var(
        self,
        key: str,
        var: Var,
        data: dict[str, Any],
        raise_missing: bool,
    ) -> tuple[Any | None, set[str]]:
        """Pack a component variable from unpacked data.

        Args:
            key: Variable key.
            var: Variable with components.
            data: Unpacked data dict.
            raise_missing: Whether to raise on missing data.

        Returns:
            tuple: (packed_value or None, set of processed keys)

        Raises:
            KeyError: If components are partially or fully missing
                per raise_missing flag.
        """
        comp_keys = [f"{key}__{comp}" for comp in var.components]
        missing = [k for k in comp_keys if k not in data]
        any_present = any(k in data for k in comp_keys)

        if missing:
            if any_present:
                # Partial - always an error
                raise KeyError(
                    f"Missing component keys for '{key}': "
                    f"{missing}. Expected keys: {comp_keys}."
                )
            if raise_missing:
                # Fully missing with raise_missing=True
                raise KeyError(
                    f"Missing variable '{key}' in data. "
                    f"Expected component keys: {comp_keys}."
                )
            # Fully missing with raise_missing=False - skip
            return None, set()

        # All components present - pack them
        comp_data = [data[k] for k in comp_keys]
        all_scalar = all(
            isinstance(v, int | float | np.number) for v in comp_data
        )
        all_array = all(
            isinstance(v, list | np.ndarray) for v in comp_data
        )

        if all_scalar:
            packed_value = comp_data
        elif all_array:
            arr = np.array(comp_data)
            if var.component_axis != 0:
                arr = np.moveaxis(arr, 0, var.component_axis)
            packed_value = arr.tolist()
        else:
            packed_value = comp_data

        return packed_value, set(comp_keys)

    def pack(
        self, data: dict[str, Any], raise_missing: bool = False,
    ) -> dict[str, Any]:
        """Reconstruct original structure from unpacked data.

        This is the reverse of unpack(). Takes data with component
        variables expanded (e.g., force__x, force__y, force__z) and
        reconstructs the original structure (e.g., force: [x, y, z]).

        Args:
            data: Dictionary with unpacked component keys.
            raise_missing: If True, raise KeyError for variables in VarSet
                that are missing from data. If False, silently skip missing
                variables. Defaults to False.

        Returns:
            dict[str, Any]: Dictionary with original structure restored.

        Raises:
            TypeError: If data is not a dict.
            KeyError: If required component keys are missing (when the
                variable is present), or if raise_missing=True and
                variables are missing from data.

        Examples:
            >>> # After unpacking
            >>> unpacked = {
            ...     "temp": 25, "force__x": 10,
            ...     "force__y": 20, "force__z": 30
            ... }
            >>> packed = varset.pack(unpacked)
            >>> packed
            {"temp": 25, "force": [10, 20, 30]}
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"Data must be a dict, got {type(data).__name__}."
            )

        result = {}
        processed_keys = set()

        for key, var in self._vars.items():
            if var.components:
                packed_value, keys = self._pack_component_var(
                    key, var, data, raise_missing
                )
                if packed_value is not None:
                    result[key] = packed_value
                    processed_keys.update(keys)
            else:
                # Non-component variable
                if key not in data:
                    if raise_missing:
                        raise KeyError(
                            f"Missing key '{key}' in data. "
                            f"Expected all original VarSet keys."
                        )
                    continue
                result[key] = data[key]
                processed_keys.add(key)

        # Check for extra keys
        extra = set(data.keys()) - processed_keys
        if extra:
            raise KeyError(
                f"Extra keys in data not in VarSet: {sorted(extra)}."
            )

        return result

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

        Raises:
            TypeError: If data is not a dict.
            KeyError: If data keys don't match VarSet keys.
            ValueError: If data is empty.
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"Data must be a dict, got {type(data).__name__}. "
                f"For multiple records, pass a list of dicts."
            )
        if not data:
            raise ValueError(
                "Cannot create DataFrame from empty data dict."
            )
        
        # Check for missing and extra keys
        data_keys = set(data.keys())
        var_keys = set(self._vars.keys())
        missing = var_keys - data_keys
        extra = data_keys - var_keys
        
        if missing or extra:
            msg_parts = []
            if missing:
                msg_parts.append(
                    f"Missing keys in data: {sorted(missing)}"
                )
            if extra:
                msg_parts.append(
                    f"Extra keys in data: {sorted(extra)}"
                )
            msg = ". ".join(msg_parts)
            msg += f". Expected keys: {sorted(var_keys)}."
            raise KeyError(msg)
        
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
            TypeError: If data_list is not a list or contains non-dict items.
            ValueError: If the data list is empty.
            KeyError: If record keys don't match VarSet keys.
        """
        if not isinstance(data_list, list):
            raise TypeError(
                f"Data must be a list of dicts, got "
                f"{type(data_list).__name__}. "
                f"For a single record, pass a dict directly."
            )
        if not data_list:
            raise ValueError(
                "Cannot create DataFrame from empty list. "
                "Provide at least one data dict."
            )
        
        var_list = None
        unpacked = []
        for i, record in enumerate(data_list):
            if not isinstance(record, dict):
                raise TypeError(
                    f"All records must be dicts. "
                    f"Record at index {i} has type {type(record).__name__}."
                )
            
            # Check for missing and extra keys
            data_keys = set(record.keys())
            var_keys = set(self._vars.keys())
            missing = var_keys - data_keys
            extra = data_keys - var_keys
            
            if missing or extra:
                msg_parts = [f"Record at index {i}:"]
                if missing:
                    msg_parts.append(
                        f"missing keys {sorted(missing)}"
                    )
                if extra:
                    msg_parts.append(
                        f"extra keys {sorted(extra)}"
                    )
                msg = " ".join(msg_parts)
                msg += f". Expected keys: {sorted(var_keys)}."
                raise KeyError(msg)
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

        Raises:
            TypeError: If data is not a dict or contains invalid VarData.
            ValueError: If data is empty.
            KeyError: If required VarData fields are missing.
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"Data must be a dict, got {type(data).__name__}."
            )
        if not data:
            raise ValueError(
                "Cannot create VarSet from empty dict."
            )
        
        try:
            return cls({
                key: Var.from_dict(var_data)
                for key, var_data in data.items()
            })
        except KeyError as e:
            raise KeyError(
                f"Invalid VarData structure: {e}"
            ) from e
        except TypeError as e:
            raise TypeError(
                f"Invalid VarData structure: {e}"
            ) from e
