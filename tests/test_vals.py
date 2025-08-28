"""Unit tests for the vals module.

This module contains tests for the Val, ValDict, and related classes.
"""

import pytest

from varmeta.vals import FloatVal, Val
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
        subvals = val1.unpack()
        print(subvals)
        assert len(subvals) == 3
        assert subvals[0].data == 10
        assert subvals[0].var.name == "force - x"
        assert subvals[1].data == 20
        assert subvals[1].var.name == "force - y"
        assert subvals[2].data == 30
        assert subvals[2].var.name == "force - z"

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
