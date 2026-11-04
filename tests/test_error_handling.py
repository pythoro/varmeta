"""Unittests for error handling and helpful error messages."""

import pytest

import varmeta as vm


class TestVarSetConstruction:
    """Test error handling during VarSet construction."""

    def test_empty_dict(self):
        with pytest.raises(
            ValueError, match="Cannot create VarSet from empty dict"
        ):
            vm.VarSet({})

    def test_empty_list(self):
        with pytest.raises(
            ValueError, match="Cannot create VarSet from empty sequence"
        ):
            vm.VarSet([])

    def test_wrong_type(self):
        # Strings are sequences, so this triggers the sequence validation
        with pytest.raises(
            TypeError, match="Sequence items must be Var instances"
        ):
            vm.VarSet("not a sequence or dict")

    def test_non_var_in_dict(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        with pytest.raises(
            TypeError, match="Dict values must be Var instances"
        ):
            vm.VarSet({"temp": temp, "bad": "not a Var"})

    def test_non_var_in_sequence(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        with pytest.raises(
            TypeError, match="Sequence items must be Var instances"
        ):
            vm.VarSet([temp, "not a Var"])

    def test_duplicate_keys_in_sequence(self):
        temp1 = vm.Var(
            key="temp", name="Temperature 1", units="C", description="Temp 1"
        )
        temp2 = vm.Var(
            key="temp", name="Temperature 2", units="C", description="Temp 2"
        )
        with pytest.raises(
            ValueError, match="Duplicate key 'temp' found in Var sequence"
        ):
            vm.VarSet([temp1, temp2])


class TestVarFromDict:
    """Test error handling in Var.from_dict()."""

    def test_not_a_dict(self):
        with pytest.raises(TypeError, match="Expected dict"):
            vm.Var.from_dict("not a dict")

    def test_missing_required_fields(self):
        with pytest.raises(
            KeyError, match="Missing required fields.*\\['name', 'units'\\]"
        ):
            vm.Var.from_dict({"key": "temp", "description": "Temperature"})

    def test_missing_single_field(self):
        with pytest.raises(
            KeyError, match="Missing required fields.*\\['units'\\]"
        ):
            vm.Var.from_dict(
                {
                    "key": "temp",
                    "name": "Temperature",
                    "description": "Temperature",
                }
            )


class TestVarSetFromDict:
    """Test error handling in VarSet.from_dict()."""

    def test_not_a_dict(self):
        with pytest.raises(TypeError, match="Data must be a dict"):
            vm.VarSet.from_dict("not a dict")

    def test_empty_dict(self):
        with pytest.raises(
            ValueError, match="Cannot create VarSet from empty dict"
        ):
            vm.VarSet.from_dict({})

    def test_invalid_vardata(self):
        with pytest.raises(KeyError, match="Invalid VarData structure"):
            vm.VarSet.from_dict(
                {
                    "temp": {"key": "temp"}  # Missing required fields
                }
            )


class TestVarSetUnpack:
    """Test error handling in VarSet.unpack()."""

    def test_not_a_dict(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(TypeError, match="Data must be a dict"):
            varset.unpack("not a dict")

    def test_missing_keys(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        pressure = vm.Var(
            key="pressure", name="Pressure", units="Pa", description="Pressure"
        )
        varset = vm.VarSet([temp, pressure])
        with pytest.raises(
            KeyError, match="Missing keys in data.*\\['pressure'\\]"
        ):
            varset.unpack({"temp": 25.0})

    def test_extra_keys(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            KeyError, match="Extra keys in data.*\\['humidity'\\]"
        ):
            varset.unpack({"temp": 25.0, "humidity": 50.0}, raise_extra=True)

    def test_missing_and_extra_keys(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        pressure = vm.Var(
            key="pressure", name="Pressure", units="Pa", description="Pressure"
        )
        varset = vm.VarSet([temp, pressure])
        with pytest.raises(KeyError, match="Missing keys.*Extra keys"):
            varset.unpack({"temp": 25.0, "humidity": 50.0}, raise_extra=True)

    def test_extra_keys_no_raise_extra(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        # Should not raise an error because raise_extra is False by default
        varset.unpack({"temp": 25.0, "humidity": 50.0})


class TestVarSetToDataFrameDict:
    """Test error handling in VarSet.to_dataframe() with single dict."""

    def test_not_a_dict(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            TypeError, match="Data must be a dict.*For multiple records"
        ):
            varset.to_dataframe("not a dict")

    def test_empty_dict(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            ValueError, match="Cannot create DataFrame from empty data dict"
        ):
            varset.to_dataframe({})

    def test_missing_keys(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        pressure = vm.Var(
            key="pressure", name="Pressure", units="Pa", description="Pressure"
        )
        varset = vm.VarSet([temp, pressure])
        with pytest.raises(
            KeyError, match="Missing keys in data.*\\['temp'\\]"
        ):
            varset.to_dataframe({"pressure": 101325})

    def test_extra_keys(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            KeyError, match="Extra keys in data.*\\['humidity'\\]"
        ):
            varset.to_dataframe({"temp": 25.0, "humidity": 50.0})


class TestVarSetToDataFrameRecords:
    """Test error handling in VarSet.to_dataframe() with list of dicts."""

    def test_not_a_list(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        # Pass an integer - triggers dict validation first
        with pytest.raises(
            TypeError, match="Data must be a dict.*For multiple records"
        ):
            varset.to_dataframe(123)

    def test_empty_list(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            ValueError, match="Cannot create DataFrame from empty list"
        ):
            varset.to_dataframe([])

    def test_non_dict_in_list(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            TypeError, match="All records must be dicts.*Record at index 1"
        ):
            varset.to_dataframe([{"temp": 25.0}, "not a dict"])

    def test_missing_keys_in_record(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        pressure = vm.Var(
            key="pressure", name="Pressure", units="Pa", description="Pressure"
        )
        varset = vm.VarSet([temp, pressure])
        with pytest.raises(
            KeyError, match="Record at index 1.*missing keys.*\\['pressure'\\]"
        ):
            varset.to_dataframe(
                [
                    {"temp": 25.0, "pressure": 101325},
                    {"temp": 30.0},  # Missing pressure
                ]
            )

    def test_extra_keys_in_record(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        varset = vm.VarSet([temp])
        with pytest.raises(
            KeyError, match="Record at index 0.*extra keys.*\\['humidity'\\]"
        ):
            varset.to_dataframe([{"temp": 25.0, "humidity": 50.0}])


class TestVarUnpack:
    """Test error handling in Var.unpack()."""

    def test_no_components(self):
        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        with pytest.raises(
            ValueError, match="Var 'temp' has no components to unpack"
        ):
            temp.unpack([25.0])

    def test_scalar_value(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        with pytest.raises(
            ValueError, match="Cannot unpack scalar value for Var 'force'"
        ):
            force.unpack(25.0)

    def test_component_count_mismatch_1d(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        with pytest.raises(
            ValueError, match="Component count mismatch.*Expected 3 components"
        ):
            force.unpack([10.0, 20.0])  # Only 2 values, need 3

    def test_component_count_mismatch_multidim(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
            component_axis=1,
        )
        with pytest.raises(
            ValueError, match="Component count mismatch.*Expected 3 components"
        ):
            force.unpack(
                [[10.0, 20.0], [30.0, 40.0]]
            )  # Only 2 along axis 1, need 3

    def test_axis_out_of_bounds(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
            component_axis=2,  # Out of bounds for 2D array
        )
        with pytest.raises(
            ValueError, match="Component axis 2 is out of bounds"
        ):
            force.unpack([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]])


class TestVarsToMultiIndexData:
    """Test error handling in _vars_to_multi_index_data()."""

    def test_invalid_attr_names(self):
        from varmeta.vars import _vars_to_multi_index_data

        temp = vm.Var(
            key="temp", name="Temperature", units="C", description="Temp"
        )
        with pytest.raises(
            AttributeError,
            match="Invalid attribute names.*\\['invalid_attr'\\]",
        ):
            _vars_to_multi_index_data([temp], attrs=["key", "invalid_attr"])
