"""Unittests for documentation examples."""

import pytest

import varmeta as vm

TEMP = "temp"
FORCE = "force"


@pytest.fixture
def temperature():
    return vm.Var(
        key=TEMP,
        name="Temperature",
        units="Celsius",
        description="Ambient temperature",
        components=None,
    )


@pytest.fixture
def force():
    return vm.Var(
        key=FORCE,
        name="Force",
        units="N",
        description="Force vector",
        components=("x", "y", "z"),
        component_axis=1,
    )


@pytest.fixture
def varset(temperature, force):
    return vm.VarSet([temperature, force])


class TestDocExamples:
    def test_var_creation(self, temperature, force, varset):
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        output = repr(varset) + "\n" + repr(data_dct)
        expected_output = """{'temp': Temperature [Celsius], 'force': Force [N]}
{'temp': 25.0, 'force': [10.0, 20.0, 30.0]}"""
        assert output == expected_output

    def test_unpack_1(self, varset):
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        vars, vals = varset.unpack(data_dct)
        print(vars)
        print(vals)
        output = repr(vars) + "\n" + repr(vals)
        expected_output = """{'temp': Temperature [Celsius], 'force__x': Force - x [N], 'force__y': Force - y [N], 'force__z': Force - z [N]}
{'temp': 25.0, 'force__x': 10.0, 'force__y': 20.0, 'force__z': 30.0}"""
        assert output == expected_output

    def test_dict_to_df(self, varset):
        data_dct = {FORCE: [[200, 250, -30], [300, 350, -100]], TEMP: [30, 40]}
        df = varset.to_dataframe(data_dct)
        print(df)
        data_dct = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
        df2 = varset.to_dataframe(data_dct)
        print(df2)
        output = repr(df) + "\n" + repr(df2)
        expected_output = """key    force__x  force__y  force__z        temp
name  Force - x Force - y Force - z Temperature
units         N         N         N     Celsius
0           200       250       -30          30
1           300       350      -100          40
key          temp  force__x  force__y  force__z
name  Temperature Force - x Force - y Force - z
units     Celsius         N         N         N
0              30       200       250       -30
1              40       300       350      -100"""
        assert output == expected_output

    def test_records_to_df(self, varset):
        data_dict_lst = [
            {FORCE: [200, 250, -30], TEMP: 30},
            {FORCE: [300, 350, -100], TEMP: 40},
        ]
        df = varset.to_dataframe(data_dict_lst)
        print(df)
        output = repr(df)
        expected_output = """key    force__x  force__y  force__z        temp
name  Force - x Force - y Force - z Temperature
units         N         N         N     Celsius
0           200       250       -30          30
1           300       350      -100          40"""
        assert output == expected_output

    def test_serialisation(self, varset):
        var_data = varset.to_dict()
        print(var_data)
        varset_recreated = vm.VarSet.from_dict(var_data)
        for k in varset_recreated:
            assert varset_recreated[k] == varset[k]

    def test_describing_table_columns(self, varset):
        extra = vm.Var(
            key="speed", name="Speed", units="m/s", description="Speed"
        )
        combined = varset | vm.VarSet([extra])

        naming = vm.ColumnNaming(
            separator="_",
            prefixes=("loads_",),
            derived=("mag",),
        )
        lines = []
        for column in ["temp", "loads_force_x", "force_mag", "speed", "other"]:
            match = combined.match_column(column, naming)
            if match is None:
                lines.append(f"{column}: no match")
            else:
                lines.append(
                    f"{column}: {match.var.key} {match.component} "
                    f"[{match.var.units}]"
                )
        expected_output = """temp: temp None [Celsius]
loads_force_x: force x [N]
force_mag: force mag [N]
speed: speed None [m/s]
other: no match"""
        assert "\n".join(lines) == expected_output
