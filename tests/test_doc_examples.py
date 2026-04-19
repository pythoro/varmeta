"""Unittests for documentation examples."""

import pytest
from pytest import approx

import varmeta as vm

TEMP = "temp"
FORCE = "force"
VELOCITY = "vel"
MASS = "mass"


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


class TestDocExamples:
    def test_var_creation(self, temperature, force):
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})

        output = repr(var_dct) + "\n" + repr(data_dct)
        expected_output = """{'temp': Temperature [Celsius], 'force': Force [N]}
{'temp': 25.0, 'force': [10.0, 20.0, 30.0]}"""
        assert output == expected_output

    def test_unpack_1(self, temperature, force):
        # Vector variable (e.g., 3D force)
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        vars, vals = vm.unpack(var_dct, data_dct)
        print(vars)
        # {'temp': Temperature [Celsius], 'force_x': Force - x [N], 'force_y': Force - y [N], 'force_z': Force - z [N]}
        print(vals)
        # {'temp': 25.0, 'force_x': 10.0, 'force_y': 20.0, 'force_z': 30.0}
        output = repr(vars) + "\n" + repr(vals)
        expected_output = """{'temp': Temperature [Celsius], 'force_x': Force - x [N], 'force_y': Force - y [N], 'force_z': Force - z [N]}
{'temp': 25.0, 'force_x': 10.0, 'force_y': 20.0, 'force_z': 30.0}"""
        assert output == expected_output

    def test_dict_to_df(self, temperature, force):
        # Vector variable (e.g., 3D force)
        data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        data_dct = {FORCE: [[200, 250, -30], [300, 350, -100]], TEMP: [30, 40]}
        df = vm.dict_to_df(var_dct, data_dct)
        print(df)
        # key     force_x   force_y   force_z        temp
        # name  Force - x Force - y Force - z Temperature
        # units         N         N         N     Celsius
        # 0           200       250       -30          30
        # 1           300       350      -100          40
        data_dct = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
        df2 = vm.dict_to_df(var_dct, data_dct)
        print(df2)
        # key          temp   force_x   force_y   force_z
        # name  Temperature Force - x Force - y Force - z
        # units     Celsius         N         N         N
        # 0              30       200       250       -30
        # 1              40       300       350      -100
        output = repr(df) + "\n" + repr(df2)
        expected_output = """key     force_x   force_y   force_z        temp
name  Force - x Force - y Force - z Temperature
units         N         N         N     Celsius
0           200       250       -30          30
1           300       350      -100          40
key          temp   force_x   force_y   force_z
name  Temperature Force - x Force - y Force - z
units     Celsius         N         N         N
0              30       200       250       -30
1              40       300       350      -100"""
        assert output == expected_output

    def test_records_to_df(self, temperature, force):
        # Vector variable (e.g., 3D force)
        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        data_dict_lst = [
            {FORCE: [200, 250, -30], TEMP: 30},
            {FORCE: [300, 350, -100], TEMP: 40},
        ]
        df = vm.records_to_df(var_dct, data_dict_lst)
        print(df)
        # key     force_x   force_y   force_z        temp
        # name  Force - x Force - y Force - z Temperature
        # units         N         N         N     Celsius
        # 0           200       250       -30          30
        # 1           300       350      -100          40
        output = repr(df)
        expected_output = """key     force_x   force_y   force_z        temp
name  Force - x Force - y Force - z Temperature
units         N         N         N     Celsius
0           200       250       -30          30
1           300       350      -100          40"""
        assert output == expected_output

    def test_serialisation(self, temperature, force):
        var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
        var_data = vm.vars_to_dict(var_dct)
        print(var_data)
        # {'temp': {'key': 'temp', 'name': 'Temperature', 'units': 'Celsius', 'description': 'Ambient temperature', 'components': None, 'component_axis': 0, 'data_type': 'object'}, 'force': {'key': 'force', 'name': 'Force', 'units': 'N', 'description': 'Force vector', 'components': ('x', 'y', 'z'), 'component_axis': 1, 'data_type': 'object'}}
        var_dct_recreated = vm.vars_from_dict(var_data)
        for k, v in var_dct_recreated.items():
            print(f"{k}: {'matches!' if v == var_dct[k] else 'differs!'}")
        # Output
        # temp: match is True
        # force: match is True
        for k, v in var_dct_recreated.items():
            assert v == var_dct[k]


@pytest.fixture
def val_dict_1():
    dct = {
            "temp": vm.ValData({
                "key": "temp",
                "name": "Temperature",
                "units": "Celsius",
                "description": "Ambient temperature",
                "components": None,
                "component_axis": 0,
                "data_type": "float",
                "value": 25.0,
            }),
            "force": vm.ValData({
                "key": "force",
                "name": "Force",
                "units": "N",
                "description": "Force vector",
                "components": ("x", "y", "z"),
                "component_axis": 1,
                "data_type": "list[float]",
                "value": [10.0, 20.0, 30.0],
            }),
        }
    return vm.ValDict.from_valdata_dict(dct)

class TestValDictDocExamples:
    def test_from_valdata_dict(self, temperature, force):
        dct = {
            "temp": vm.ValData({
                "key": "temp",
                "name": "Temperature",
                "units": "Celsius",
                "description": "Ambient temperature",
                "components": None,
                "component_axis": 0,
                "data_type": "float",
                "value": 25.0,
            }),
            "force": vm.ValData({
                "key": "force",
                "name": "Force",
                "units": "N",
                "description": "Force vector",
                "components": ("x", "y", "z"),
                "component_axis": 1,
                "data_type": "list[float]",
                "value": [10.0, 20.0, 30.0],
            }),
        }
        val_dict = vm.ValDict.from_valdata_dict(dct)
        print(val_dict)
        dct_recreated = val_dict.to_valdata_dict()
        print(dct_recreated)
        for key, subdct in dct_recreated.items():
            for k, v in subdct.items():
                assert v == approx(dct[key][k])

    def test_unpack(self, val_dict_1):
        unpacked = val_dict_1.unpack()
        print(unpacked)
        expected_output = """{Temperature [Celsius]: 25.0, Force - x [N]: 10.0, Force - y [N]: 20.0, Force - z [N]: 30.0}"""
        output = repr(unpacked)
        assert output == expected_output


    def test_to_df(self, val_dict_1):
        df = val_dict_1.to_df()
        print(df)
        expected_output = """{Temperature [Celsius]: 25.0, Force - x [N]: 10.0, Force - y [N]: 20.0, Force - z [N]: 30.0}"""
        output = repr(df)
        assert output == expected_output