"""Unittests for core module."""

import pandas as pd

from varmeta import Var, VarSet
from varmeta.vars import _vars_to_multi_index_data


class Test_Pandas_Integration:
    """Test usage as indices of pandas DataFrame."""

    def test_var_in_dct(self):
        var = Var(
            key="windspeed",
            name="wind_speed",
            units="m/s",
            description="Wind speed at 10m",
            components=None,
        )
        df = pd.DataFrame({var: [5.0, 10.0]})
        print(df)
        assert df[var].tolist() == [5.0, 10.0]
        assert df.shape == (2, 1)

    def test_var_as_index(self):
        var = Var(
            key="windspeed",
            name="wind_speed",
            units="m/s",
            description="Wind speed at 10m",
            components=None,
        )
        df = pd.DataFrame({"data": [5.0, 10.0]}, index=[var, var])
        print(df)
        assert df.index[0] == var
        assert df.index[1] == var
        assert df.shape == (2, 1)

    def test_var_as_columns(self):
        var = Var(
            key="insol",
            name="solar_radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        df = pd.DataFrame({var: [200, 300], var2: [3, 4]})
        print(df)
        assert var in df.columns
        assert df[var].tolist() == [200, 300]
        assert df[var2].tolist() == [3, 4]
        assert df.shape == (2, 2)

    def test_to_csv(self):
        var = Var(
            key="insol",
            name="solar_radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        df = pd.DataFrame({var: [200, 300], var2: [3, 4]})
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = "solar_radiation [W/m^2],mass [kg]\n200,3\n300,4\n"
        assert csv_output == expected_csv

    def test_vars_to_multi_index_data(self):
        var = Var(
            key="insol",
            name="solar radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        vars = [var, var2]
        tuples, names = _vars_to_multi_index_data(vars)
        columns = pd.MultiIndex.from_tuples(tuples, names=names)
        df = pd.DataFrame({"insol": [200, 300], "m": [3, 4]})
        df.columns = columns
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = (
            "insol,m\nsolar radiation,mass\nW/m^2,kg\n200,3\n300,4\n"
        )
        assert csv_output == expected_csv

    def test_dict_to_df(self):
        var = Var(
            key="insol",
            name="solar radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        varset = VarSet({"insol": var, "m": var2})
        data_dct = {"insol": [200, 300], "m": [3, 4]}
        df = varset.to_dataframe(data_dct)
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = (
            "insol,m\nsolar radiation,mass\nW/m^2,kg\n200,3\n300,4\n"
        )
        assert csv_output == expected_csv

    def test_dict_to_df_with_unpack(self):
        var = Var(
            key="insol",
            name="solar radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=("morning", "afternoon"),
            component_axis=1,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        varset = VarSet({"insol": var, "m": var2})
        data_dct = {"insol": [[200, 250], [300, 350]], "m": [3, 4]}
        df = varset.to_dataframe(data_dct)
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = "insol__morning,insol__afternoon,m\nsolar radiation - morning,solar radiation - afternoon,mass\nW/m^2,W/m^2,kg\n200,250,3\n300,350,4\n"  # NoQA: E501
        assert csv_output == expected_csv

    def test_records_to_df_with_unpack(self):
        var = Var(
            key="insol",
            name="solar radiation",
            units="W/m^2",
            description="Solar radiation at surface",
            components=("morning", "afternoon"),
            component_axis=1,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            description="Mass of the object",
            components=None,
        )
        varset = VarSet({"insol": var, "m": var2})
        data_dict_lst = [
            {"insol": [200, 250], "m": 3},
            {"insol": [300, 350], "m": 4},
        ]
        df = varset.to_dataframe(data_dict_lst)
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = "insol__morning,insol__afternoon,m\nsolar radiation - morning,solar radiation - afternoon,mass\nW/m^2,W/m^2,kg\n200,250,3\n300,350,4\n"  # NoQA: E501
        assert csv_output == expected_csv

    def test_single_row_with_scalar_and_components(self):
        temp = Var(
            key="temp",
            name="Temperature",
            units="Celsius",
            description="Ambient temperature",
            components=None,
        )
        force = Var(
            key="force",
            name="Force",
            units="N",
            description="Force vector",
            components=("x", "y", "z"),
            component_axis=1,
        )
        varset = VarSet([temp, force])
        # Single row: scalar + component that unpacks to scalars
        data = {"temp": 25.0, "force": [10.0, 20.0, 30.0]}
        df = varset.to_dataframe(data)
        print(df)
        
        # Should produce a single-row DataFrame with 4 columns
        assert df.shape == (1, 4)
        
        # Access values by position since we have MultiIndex columns
        assert df.iloc[0, 0] == 25.0  # temp
        assert df.iloc[0, 1] == 10.0  # force_x
        assert df.iloc[0, 2] == 20.0  # force_y
        assert df.iloc[0, 3] == 30.0  # force_z
