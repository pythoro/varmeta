"""Unit tests for the vals module.

This module contains tests for the Val, ValDict, and related classes.
"""

import pytest

from varmeta.vals import FloatVal, Val, ValDict
from varmeta.vars import Var


@pytest.fixture
def force():
    return Var(
        key="F",
        name="force",
        units="N",
        desciption="A force",
        components=None,
    )


class TestVal:
    """Tests for the Val class."""

    def test_basic(self) -> None:
        """Test basic Val creation and attribute access."""
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=None,
        )
        val1 = Val(data=10, var=force)
        assert val1.data == 10
        assert val1.var == force

    def test_unpack(self) -> None:
        """Test unpacking a Val with components."""
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        val1 = Val(data=[10, 20, 30], var=force)
        unpacked_vals = val1.unpack()
        assert len(unpacked_vals) == 3
        assert unpacked_vals[0].data == 10
        assert unpacked_vals[0].var.name == "force x"
        assert unpacked_vals[1].data == 20
        assert unpacked_vals[1].var.name == "force y"
        assert unpacked_vals[2].data == 30
        assert unpacked_vals[2].var.name == "force z"

    def test_with_typed_var(self) -> None:
        """Test Val with typed Var."""
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=None,
            data_type="float",
        )
        # No type errors
        Val(data=5.4, var=force)
        with pytest.raises(TypeError):
            Val(data="garbage", var=force)

    def test_intval_generic_types(self, force) -> None:
        """Test Val with generic types."""
        val1: Val[int] = Val(data=42, var=force)  # Should pass pylance
        val2: Val[str] = Val(data=42, var=force)  # Should fail pylance
        vals = [val1, val2]  # noqa: F841

    def test_floatval(self, force) -> None:
        """Test FloatVal with float data."""
        # No type errors
        val1 = FloatVal(data=3.14, var=force)
        assert isinstance(val1.data, float)
        assert val1.data == 3.14
        with pytest.raises(TypeError):
            FloatVal(data="this_is_a_string", var=force)  # type: ignore


class TestValDict:
    """Tests for the ValDict class."""

    def setup_method(self) -> None:
        """Setup test variables for each test."""
        self.var1 = Var(
            key="k", name="a", units="m", desciption="desc", components=None
        )
        self.var2 = Var(
            key="b", name="b", units="kg", desciption="desc", components=None
        )

    def test_setitem_valid(self) -> None:
        """Test setting a valid Var key in ValDict."""
        d = ValDict()
        d[self.var1] = 1
        assert d[self.var1] == 1

    def test_setitem_invalid_key(self) -> None:
        """Test that setting a non-Var key raises TypeError."""
        d = ValDict()
        with pytest.raises(TypeError):
            d["not_a_var"] = 1  # type: ignore

    def test_init_with_dict(self) -> None:
        """Test initializing ValDict with a dict of Var keys."""
        d = ValDict({self.var1: 2, self.var2: 3})
        assert d[self.var1] == 2
        assert d[self.var2] == 3

    def test_init_with_kwargs(self) -> None:
        """Test that initializing ValDict without Var keys raises TypeError."""
        # kwargs keys are always strings, so should fail
        with pytest.raises(TypeError):
            ValDict(not_a_var=1)

    def test_update_valid(self) -> None:
        """Test updating ValDict with valid Var keys."""
        d = ValDict()
        d.update({self.var1: 5})
        assert d[self.var1] == 5

    def test_update_invalid_key(self) -> None:
        """Test that updating ValDict with a non-Var key raises TypeError."""
        d = ValDict()
        with pytest.raises(TypeError):
            d.update({"not_a_var": 1})

    def test_unpack(self) -> None:
        """Test unpacking with non-unpackable Vars raises ValueError."""
        # Only works if Var has components, so just test empty for now
        d = ValDict({self.var1: 1})
        with pytest.raises(ValueError):
            d.unpack()

    def test_key_conflict(self) -> None:
        """Test that conflicting Vars objects raises KeyError."""
        d = ValDict()
        var1 = Var(
            key="k", name="a", units="m", desciption="desc", components=None
        )
        var2 = Var(
            key="k", name="b", units="kg", desciption="desc", components=None
        )
        d[var1] = 1
        with pytest.raises(KeyError):
            d[var2] = 2

    def test_find_var(self) -> None:
        """Test finding a Var by key in ValDict."""
        d = ValDict({self.var1: 1, self.var2: 2})
        found_var = d.find_var("k")
        assert found_var == self.var1
        with pytest.raises(KeyError):
            d.find_var("non_existent")

    def test_find(self) -> None:
        """Test finding a value by Var key in ValDict."""
        d = ValDict({self.var1: 1, self.var2: 2})
        found_data = d.find("k")
        assert found_data == 1
        found_data = d.find("b")
        assert found_data == 2
