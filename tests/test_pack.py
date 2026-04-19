"""Unittests for VarSet.pack() method."""

import numpy as np
import pytest

import varmeta as vm


class TestVarSetPack:
    """Test VarSet.pack() functionality."""

    def test_pack_scalar_components(self):
        """Test packing scalar component values."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        # Unpacked data
        unpacked = {"temp": 25.0, "force__x": 10.0, "force__y": 20.0, "force__z": 30.0}

        # Pack it back
        packed = varset.pack(unpacked)

        assert packed == {"temp": 25.0, "force": [10.0, 20.0, 30.0]}

    def test_pack_array_components(self):
        """Test packing array component values."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
            component_axis=1,  # Components along axis 1
        )
        varset = vm.VarSet([temp, force])

        # Unpacked data with arrays
        unpacked = {
            "temp": [25.0, 30.0],
            "force__x": [10.0, 40.0],
            "force__y": [20.0, 50.0],
            "force__z": [30.0, 60.0],
        }

        # Pack it back
        packed = varset.pack(unpacked)

        assert packed["temp"] == [25.0, 30.0]
        assert packed["force"] == [[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]

    def test_pack_with_component_axis_1(self):
        """Test packing with non-zero component axis."""
        insol = vm.Var(
            key="insol",
            name="Solar Radiation",
            units="W/m^2",
            description="Solar radiation",
            components=("morning", "afternoon"),
            component_axis=1,
        )
        varset = vm.VarSet([insol])

        # Unpacked data - 2 records, 2 components each
        unpacked = {
            "insol__morning": [200, 300],
            "insol__afternoon": [250, 350],
        }

        # Pack it back
        packed = varset.pack(unpacked)

        # With component_axis=1, the shape should be [2 records, 2 components]
        expected = [[200, 250], [300, 350]]
        assert packed["insol"] == expected

    def test_pack_with_component_axis_0(self):
        """Test packing with component_axis=0 (components along first dimension)."""
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
            component_axis=0,  # Components along axis 0
        )
        varset = vm.VarSet([force])

        # Unpacked data - each component has 2 values
        unpacked = {
            "force__x": [10.0, 40.0],
            "force__y": [20.0, 50.0],
            "force__z": [30.0, 60.0],
        }

        # Pack it back
        packed = varset.pack(unpacked)

        # With component_axis=0, shape should be [3 components, 2 records]
        expected = [[10.0, 40.0], [20.0, 50.0], [30.0, 60.0]]
        assert packed["force"] == expected

    def test_pack_no_components(self):
        """Test packing with no component variables."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        pressure = vm.Var(key="pressure", name="Pressure", units="Pa", description="Pressure")
        varset = vm.VarSet([temp, pressure])

        data = {"temp": 25.0, "pressure": 101325}
        packed = varset.pack(data)

        assert packed == data

    def test_pack_mixed_scalars_and_components(self):
        """Test packing with mix of scalar and component variables."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y"),
        )
        mass = vm.Var(key="mass", name="Mass", units="kg", description="Mass")
        varset = vm.VarSet([temp, force, mass])

        unpacked = {
            "temp": 25.0,
            "force__x": 10.0,
            "force__y": 20.0,
            "mass": 5.0,
        }

        packed = varset.pack(unpacked)

        assert packed == {"temp": 25.0, "force": [10.0, 20.0], "mass": 5.0}

    def test_pack_round_trip_with_unpack(self):
        """Test that pack(unpack(data)) == data."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        original = {"temp": 25.0, "force": [10.0, 20.0, 30.0]}

        # Unpack
        _, unpacked = varset.unpack(original)

        # Pack back
        packed = varset.pack(unpacked)

        assert packed == original

    def test_pack_numpy_arrays(self):
        """Test packing with numpy arrays."""
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
            component_axis=1,  # Components along axis 1
        )
        varset = vm.VarSet([force])

        unpacked = {
            "force__x": np.array([10.0, 40.0]),
            "force__y": np.array([20.0, 50.0]),
            "force__z": np.array([30.0, 60.0]),
        }

        packed = varset.pack(unpacked)

        # Should return lists, not numpy arrays
        assert isinstance(packed["force"], list)
        assert packed["force"] == [[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]


class TestVarSetPackErrors:
    """Test error handling in VarSet.pack()."""

    def test_pack_not_a_dict(self):
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        varset = vm.VarSet([temp])
        with pytest.raises(TypeError, match="Data must be a dict"):
            varset.pack("not a dict")

    def test_pack_missing_component_keys(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([force])

        # Missing force__z
        unpacked = {"force__x": 10.0, "force__y": 20.0}

        with pytest.raises(KeyError, match="Missing component keys.*\\['force__z'\\]"):
            varset.pack(unpacked)

    def test_pack_missing_non_component_key(self):
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        # Missing temp - should raise with raise_missing=True
        unpacked = {"force__x": 10.0, "force__y": 20.0, "force__z": 30.0}

        with pytest.raises(KeyError, match="Missing key 'temp' in data"):
            varset.pack(unpacked, raise_missing=True)

    def test_pack_missing_non_component_key_no_raise(self):
        """Test that missing non-component vars are skipped when raise_missing=False."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        # Missing temp - should skip it with raise_missing=False (default)
        unpacked = {"force__x": 10.0, "force__y": 20.0, "force__z": 30.0}
        packed = varset.pack(unpacked)

        # Should only have force, not temp
        assert packed == {"force": [10.0, 20.0, 30.0]}

    def test_pack_missing_component_variable_no_raise(self):
        """Test that missing component vars are skipped when raise_missing=False."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        # Missing force components - should skip it with raise_missing=False (default)
        unpacked = {"temp": 25.0}
        packed = varset.pack(unpacked)

        # Should only have temp, not force
        assert packed == {"temp": 25.0}

    def test_pack_missing_component_variable_raise(self):
        """Test that missing component vars raise when raise_missing=True."""
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([temp, force])

        # Missing force components
        unpacked = {"temp": 25.0}

        with pytest.raises(KeyError, match="Missing variable 'force' in data"):
            varset.pack(unpacked, raise_missing=True)

    def test_pack_partial_component_keys_always_raises(self):
        """Test that partial component keys always raise, regardless of raise_missing."""
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y", "z"),
        )
        varset = vm.VarSet([force])

        # Only some components present - should always raise
        unpacked = {"force__x": 10.0, "force__y": 20.0}  # Missing force__z

        with pytest.raises(KeyError, match="Missing component keys.*\\['force__z'\\]"):
            varset.pack(unpacked, raise_missing=False)

        with pytest.raises(KeyError, match="Missing component keys.*\\['force__z'\\]"):
            varset.pack(unpacked, raise_missing=True)

    def test_pack_extra_keys(self):
        temp = vm.Var(key="temp", name="Temperature", units="C", description="Temp")
        varset = vm.VarSet([temp])

        # Extra key
        data = {"temp": 25.0, "extra": 100.0}

        with pytest.raises(KeyError, match="Extra keys in data.*\\['extra'\\]"):
            varset.pack(data)

    def test_pack_extra_component_keys(self):
        force = vm.Var(
            key="force",
            name="Force",
            units="N",
            description="Force",
            components=("x", "y"),
        )
        varset = vm.VarSet([force])

        # Has force__x, force__y, plus extra force__z
        data = {"force__x": 10.0, "force__y": 20.0, "force__z": 30.0}

        with pytest.raises(KeyError, match="Extra keys in data.*\\['force__z'\\]"):
            varset.pack(data)
