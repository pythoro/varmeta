"""Unittests for documentation examples."""

from varmeta.vars import Var


class TestDocExamples:
    def test_var_creation(self):
        temperature = Var(
            key="temp",
            name="Temperature",
            units="Celsius",
            desciption="Ambient temperature",
            components=None,
        )

        # Vector variable (e.g., 3D force)
        force = Var(
            key="F",
            name="Force",
            units="N",
            desciption="Force vector",
            components=("x", "y", "z"),
        )
        data = {temperature: 25.0, force: [10.0, 20.0, 30.0]}
        s = str(data)
        print(s)
        assert (
            s == "{Temperature [Celsius]: 25.0, Force [N]: [10.0, 20.0, 30.0]}"
        )

    def test_unpack(self):
        # Vector variable (e.g., 3D force)
        force = Var(
            key="F",
            name="Force",
            units="N",
            desciption="Force vector",
            components=("x", "y", "z"),
        )
        subvars, subvals = force.unpack([10.0, 20.0, 30.0])
        print(subvars)
        print(subvals)
        s = str(subvars)
        assert s == "[Force x [N], Force y [N], Force z [N]]"
        assert subvals == [10.0, 20.0, 30.0]
