"""ValDict classes for variable metadata."""

from __future__ import annotations

from . import vars
from typing import Any, TypedDict
import pandas as pd


class ValData(vars.VarData, TypedDict):
    """Variable data together with its value."""
    value: Any


class ValDict(dict[vars.Var, Any]):
    """A dictionary of Var keys to their corresponding values."""

    @classmethod
    def from_valdata_dict(cls, dct: dict[str, ValData]) -> ValDict:
        """Create a ValDict from a dictionary of variable names to ValData.

        Args:
            dct (dict[str, ValData]): A dictionary of variable names to ValData.
        
        Returns:
            ValDict: A ValDict created from the input dictionary.
        """
        out = {}
        for original in dct.values():
            d = original.copy()
            value = d.pop("value")
            var = vars.Var.from_dict(d)
            out[var] = value
        return ValDict(out)

    def split(self) -> tuple[vars.VarDict, dict[str, Any]]:
        """Split the ValDict into a VarDict and a dictionary of variable names to values.

        Returns:
            tuple[VarDict, dict[str, Any]]: A tuple containing the VarDict and the dictionary of variable names to values.
        """
        var_dct = vars.VarDict({var.key: var for var in self.keys()})
        data_dct = {var.key: val for var, val in self.items()}
        return var_dct, data_dct

    def unpack(self) -> ValDict:
        """Unpack the ValDict into a new ValDict with unpacked keys and values.

        Returns:
            ValDict: A new ValDict with unpacked keys and values.
        """
        var_dct, data_dct = self.split()
        out_vars, out_vals = vars.unpack(var_dct, data_dct)
        dct = {out_vars[key]: out_vals[key] for key in out_vars}
        return ValDict(dct)

    def to_dict(self) -> dict[str, Any]:
        """Convert the ValDict to a dictionary of variable names to values.

        Returns:
            dict[str, Any]: A dictionary of variable names to values.
        """
        unpacked = self.unpack()
        out = {}
        for var, val in unpacked.items():
            subdict = var.to_dict()
            out[var.key] = ValData({**subdict, "value": val})
        return out
    
    def to_valdata_dict(self, unpack: bool=True) -> dict[str, ValData]:
        """Convert the ValDict to a dictionary of ValData.

        Returns:
            dict[str, ValData]: A dictionary of variable names to ValData.
        """
        out = {}
        for var, val in self.items():
            subdict = var.to_dict()
            out[var.key] = ValData({**subdict, "value": val})
        return out
    


def valdict_list_to_df(
    valdict_lst: list[ValDict],
    attrs: list[str] | None = None,
) -> pd.DataFrame:
    """Convert a list of ValDicts to a pandas DataFrame.

    Args:
        valdict_lst: List of ValDict objects.
        attrs: List of Var attributes to use for MultiIndex levels.

    Returns:
        pd.DataFrame: DataFrame with MultiIndex columns based on Var metadata.
    """
    var_list = None
    unpacked = []
    for valdict in valdict_lst:
        unpacked_var_dct, subdata_dct = valdict.split()
        if var_list is None:
            var_list = [unpacked_var_dct[key] for key in subdata_dct]
        unpacked.append(subdata_dct)
    if var_list is None:
        raise ValueError("No data or malformed data provided.")
    tuples, names = vars.vars_to_multi_index_data(var_list, attrs=attrs)
    columns = pd.MultiIndex.from_tuples(tuples, names=names)
    df = pd.DataFrame.from_records(unpacked)
    df.columns = columns
    return df
