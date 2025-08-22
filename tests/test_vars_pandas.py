"""Unittests for core module."""

import pandas as pd

from varmeta import Var


class Test_Pandas_Integration:
    """Test usage as indices of pandas DataFrame."""

    def test_var_in_dct(self):
        var = Var(
            key="windspeed",
            name="wind_speed",
            units="m/s",
            desciption="Wind speed at 10m",
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
            desciption="Wind speed at 10m",
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
            desciption="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            desciption="Mass of the object",
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
            desciption="Solar radiation at surface",
            components=None,
        )
        var2 = Var(
            key="m",
            name="mass",
            units="kg",
            desciption="Mass of the object",
            components=None,
        )
        df = pd.DataFrame({var: [200, 300], var2: [3, 4]})
        print(df)
        csv_output = df.to_csv(index=False, lineterminator="\n")
        print(csv_output)
        expected_csv = "solar_radiation [W/m^2],mass [kg]\n200,3\n300,4\n"

        assert csv_output == expected_csv
