"""Unittests for core module."""

import pytest

from varmeta.vars import Store, Var


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

    def test_unpack_axis_default(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        data = [[10, 11], [20, 21], [30, 31]]
        unpacked = force.unpack(data)
        print(unpacked)
        packed_vars = list(unpacked.keys())
        packed_data = list(unpacked.values())
        assert len(packed_data) == 3
        assert packed_data[0] == [10, 11]
        assert packed_vars[0].name == "force x"
        assert packed_data[1] == [20, 21]
        assert packed_vars[1].name == "force y"
        assert packed_data[2] == [30, 31]
        assert packed_vars[2].name == "force z"

    def test_unpack_axis_1(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y"),
            component_axis=1,
        )
        data = [[10, 11], [20, 21], [30, 31]]
        unpacked = force.unpack(data)
        print(unpacked)
        packed_vars = list(unpacked.keys())
        packed_data = list(unpacked.values())
        assert len(packed_data) == 2
        assert packed_data[0] == [10, 20, 30]
        assert packed_vars[0].name == "force x"
        assert packed_data[1] == [11, 21, 31]
        assert packed_vars[1].name == "force y"

    def test_round_trip_dict(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        dct = force.to_dict()
        print(dct)
        new_var = Var(**dct)
        assert new_var == force


class TestStore:
    """Unit tests for the Store class."""

    def setup_method(self) -> None:
        self.var1 = Var(
            key="a", name="A", units="m", desciption="desc", components=None
        )
        self.var2 = Var(
            key="b", name="B", units="kg", desciption="desc", components=None
        )

    def test_add_and_get(self) -> None:
        store = Store()
        store.add(self.var1)
        store.add(self.var2)
        assert store.get("a") == self.var1
        assert store.get("b") == self.var2

    def test_add_duplicate_key(self) -> None:
        store = Store()
        store.add(self.var1)
        var1_dup = Var(
            key="a", name="A2", units="m", desciption="desc2", components=None
        )
        with pytest.raises(KeyError):
            store.add(var1_dup)

    def test_add_non_var(self) -> None:
        store = Store()
        with pytest.raises(TypeError):
            store.add("not_a_var")  # type: ignore

    def test_remove(self) -> None:
        store = Store()
        store.add(self.var1)
        store.remove("a")
        assert "a" not in store.vars
        with pytest.raises(KeyError):
            store.remove("a")

    def test_to_list(self) -> None:
        store = Store()
        store.add(self.var1)
        store.add(self.var2)
        var_list = store.to_list()
        assert self.var1 in var_list
        assert self.var2 in var_list
        assert len(var_list) == 2

    def test_to_dict(self) -> None:
        store = Store()
        store.add(self.var1)
        dct = store.to_dict()
        assert dct["a"]["name"] == "A"
        assert dct["a"]["units"] == "m"

    def test_from_dict(self) -> None:
        var_data = {
            "a": dict(
                key="a",
                name="A",
                units="m",
                desciption="desc",
                components=None,
                component_axis=0,
            ),
            "b": dict(
                key="b",
                name="B",
                units="kg",
                desciption="desc",
                components=None,
                component_axis=0,
            ),
        }
        store = Store.from_dict(var_data)
        assert store.get("a").name == "A"
        assert store.get("b").units == "kg"
