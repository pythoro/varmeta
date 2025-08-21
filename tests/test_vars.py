"""Unittests for core module."""

from varmeta.vars import Var


class TestVar:
    def test_var_creation(self):
        var = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        assert var.name == "temperature"
        assert var.units == "Celsius"
        assert var.desciption == "Ambient temperature"
        assert var.components is None

    def test_var_str(self):
        var = Var(
            key="pressure",
            name="pressure",
            units="Pascal",
            desciption="Atmospheric pressure",
            components=None,
        )
        assert str(var) == "pressure [Pascal]"

    def test_var_ordering(self):
        var1 = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        var2 = Var(
            key="pressure",
            name="pressure",
            units="Pascal",
            desciption="Atmospheric pressure",
            components=None,
        )
        assert var1 > var2  # Based on name ordering

    def test_var_equality(self):
        var1 = Var(
            key="hum",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        var2 = Var(
            key="humidity",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        assert var1 == var2

    def test_var_inequality(self):
        var1 = Var(
            key="humidity",
            name="humidity",
            units="Percent",
            desciption="Relative humidity",
            components=None,
        )
        var2 = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        assert var1 != var2

    def test_hash_with_components(self):
        var = Var(
            key="vel",
            name="velocity",
            units="m/s",
            desciption="Speed of an object",
            components=("x", "y", "z"),
        )
        assert hash(var) != 0
