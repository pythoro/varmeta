"""Tests for VarSet merging and flat column matching."""

import pytest

import varmeta as vm

TEMP = "temp"
FORCE = "force"
FRAME_ACC_X = "frame_acc_x"


@pytest.fixture
def temperature():
    return vm.Var(
        key=TEMP, name="Temperature", units="Celsius", description=""
    )


@pytest.fixture
def force():
    return vm.Var(
        key=FORCE,
        name="Force",
        units="N",
        description="",
        components=("x", "y", "z"),
    )


@pytest.fixture
def frame_acc_x():
    return vm.Var(
        key=FRAME_ACC_X, name="Frame acc x", units="m/s^2", description=""
    )


@pytest.fixture
def varset(temperature, force, frame_acc_x):
    return vm.VarSet([temperature, force, frame_acc_x])


@pytest.fixture
def naming():
    return vm.ColumnNaming(
        separator="_", prefixes=("loads_",), derived=("mag",)
    )


class TestVarSetMerge:
    def test_order_preserved(self, temperature, force, frame_acc_x):
        base = vm.VarSet([temperature, force])
        extra = vm.VarSet([frame_acc_x, temperature])
        combined = base | extra
        assert list(combined) == [TEMP, FORCE, FRAME_ACC_X]
        assert combined[FRAME_ACC_X] is frame_acc_x

    def test_inputs_unchanged(self, temperature, force, frame_acc_x):
        base = vm.VarSet([temperature, force])
        extra = vm.VarSet([frame_acc_x])
        combined = base | extra
        assert combined is not base
        assert list(base) == [TEMP, FORCE]
        assert list(extra) == [FRAME_ACC_X]

    def test_identical_duplicate_accepted(self, temperature, force):
        base = vm.VarSet([temperature, force])
        copy = vm.Var(
            key=TEMP, name="Temperature", units="Celsius", description=""
        )
        combined = base | vm.VarSet([copy])
        assert list(combined) == [TEMP, FORCE]
        assert combined[TEMP] is temperature

    def test_conflicting_duplicate_raises(self, temperature):
        base = vm.VarSet([temperature])
        other = vm.Var(
            key=TEMP, name="Temperature", units="Kelvin", description=""
        )
        with pytest.raises(ValueError, match="'temp'"):
            base | vm.VarSet([other])

    def test_non_varset_raises_type_error(self, temperature):
        base = vm.VarSet([temperature])
        with pytest.raises(TypeError):
            base | 1

    def test_non_varset_returns_not_implemented(self, temperature):
        base = vm.VarSet([temperature])
        assert base.__or__(1) is NotImplemented


class TestMatchColumn:
    @pytest.mark.parametrize(
        ("column", "key", "component", "stem"),
        [
            ("temp", TEMP, None, "temp"),
            ("force_y", FORCE, "y", "force"),
            ("force_mag", FORCE, "mag", "force"),
            ("loads_force_z", FORCE, "z", "loads_force"),
            ("frame_acc_x", FRAME_ACC_X, None, "frame_acc_x"),
        ],
    )
    def test_examples_match(
        self, varset, naming, column, key, component, stem
    ):
        match = varset.match_column(column, naming)
        assert match == vm.ColumnMatch(
            column=column, var=varset[key], component=component, stem=stem
        )
        assert match.var.key == key

    @pytest.mark.parametrize("column", ["temp_x", "force_w", "unknown"])
    def test_examples_no_match(self, varset, naming, column):
        assert varset.match_column(column, naming) is None

    def test_default_naming(self, varset):
        match = varset.match_column("force__x")
        assert match == vm.ColumnMatch("force__x", varset[FORCE], "x", FORCE)
        assert varset.match_column("force_x") is None

    def test_default_naming_matches_dataframe_keys(self, temperature):
        force = vm.Var(
            key=FORCE,
            name="Force",
            units="N",
            description="",
            components=("x", "y", "z"),
            component_axis=1,
        )
        varset = vm.VarSet([temperature, force])
        data = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
        df = varset.to_dataframe(data)
        keys = list(df.columns.get_level_values("key"))
        matches = [varset.match_column(key) for key in keys]
        assert all(m is not None for m in matches)
        assert [(m.var.key, m.component) for m in matches] == [
            (TEMP, None),
            (FORCE, "x"),
            (FORCE, "y"),
            (FORCE, "z"),
        ]

    def test_prefixes_tried_in_order(self):
        a = vm.Var(
            key="a_force",
            name="A",
            units="N",
            description="",
            components=("x",),
        )
        b = vm.Var(
            key="force", name="B", units="N", description="", components=("x",)
        )
        varset = vm.VarSet([a, b])
        first = vm.ColumnNaming(separator="_", prefixes=("pre_", "pre_a_"))
        match = varset.match_column("pre_a_force_x", first)
        assert match.var is a
        assert match.stem == "pre_a_force"
        second = vm.ColumnNaming(separator="_", prefixes=("pre_a_", "pre_"))
        assert varset.match_column("pre_a_force_x", second).var is b

    def test_second_prefix_used(self, varset):
        naming = vm.ColumnNaming(separator="_", prefixes=("a_", "b_"))
        match = varset.match_column("b_force_y", naming)
        assert match == vm.ColumnMatch(
            "b_force_y", varset[FORCE], "y", "b_force"
        )

    def test_whole_column_prefix_stripped(self, varset, naming):
        match = varset.match_column("loads_temp", naming)
        assert match == vm.ColumnMatch(
            "loads_temp", varset[TEMP], None, "loads_temp"
        )

    def test_multi_char_separator(self, varset):
        naming = vm.ColumnNaming(separator="::", derived=("mag",))
        assert varset.match_column("force::z", naming) == vm.ColumnMatch(
            "force::z", varset[FORCE], "z", "force"
        )
        assert varset.match_column("force::mag", naming).component == "mag"
        assert varset.match_column("force_z", naming) is None

    def test_split_at_last_separator(self):
        var = vm.Var(
            key="a_b", name="AB", units="", description="", components=("c",)
        )
        varset = vm.VarSet([var])
        naming = vm.ColumnNaming(separator="_")
        match = varset.match_column("a_b_c", naming)
        assert match == vm.ColumnMatch("a_b_c", var, "c", "a_b")

    def test_empty_separator_rejected(self):
        with pytest.raises(ValueError):
            vm.ColumnNaming(separator="")
