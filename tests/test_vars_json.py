import json

from varmeta.vars import Var


class TestVarJson:
    def test_var_dump(self):
        var = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )
        # Try the dump
        dump = json.dumps(var.to_dict())
        print(dump)
        assert dump == '{"key": "temp", "name": "temperature", "units": "Celsius", "desciption": "Ambient temperature", "components": null, "component_axis": 0}'

    def test_var_dump_components(self):
        var = Var(
            key="temp",
            name="temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=('x', 'y', 'z'),
            component_axis=1,
        )
        # Try the dump
        dump = json.dumps(var.to_dict())
        print(dump)
        assert dump == '{"key": "temp", "name": "temperature", "units": "Celsius", "desciption": "Ambient temperature", "components": ["x", "y", "z"], "component_axis": 1}'
