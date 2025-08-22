"""Unittests for vals module."""

import pytest

from varmeta.vals import Val, ValDict
from varmeta.vars import Var


class TestVal:
    def test_basic(self):
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

    def test_unpack(self):
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


class TestValDict:
    def setup_method(self):
        self.var1 = Var(
            key="k", name="a", units="m", desciption="desc", components=None
        )
        self.var2 = Var(
            key="b", name="b", units="kg", desciption="desc", components=None
        )

    def test_setitem_valid(self):
        d = ValDict()
        d[self.var1] = 1
        assert d[self.var1] == 1

    def test_setitem_invalid_key(self):
        d = ValDict()
        with pytest.raises(TypeError):
            d["not_a_var"] = 1  # type: ignore

    def test_init_with_dict(self):
        d = ValDict({self.var1: 2, self.var2: 3})
        assert d[self.var1] == 2
        assert d[self.var2] == 3

    def test_init_with_kwargs(self):
        # kwargs keys are always strings, so should fail
        with pytest.raises(TypeError):
            ValDict(not_a_var=1)

    def test_update_valid(self):
        d = ValDict()
        d.update({self.var1: 5})
        assert d[self.var1] == 5

    def test_update_invalid_key(self):
        d = ValDict()
        with pytest.raises(TypeError):
            d.update({"not_a_var": 1})

    def test_unpack(self):
        # Only works if Var has components, so just test empty for now
        d = ValDict({self.var1: 1})
        with pytest.raises(Exception):
            d.unpack()

    def test_key_conflict(self):
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


    def test_find_var(self):
        d = ValDict({self.var1: 1, self.var2: 2})
        found_var = d.find_var("k")
        assert found_var == self.var1
        with pytest.raises(KeyError):
            d.find_var("non_existent")

    def test_find(self):
        d = ValDict({self.var1: 1, self.var2: 2})
        found_data = d.find("k")
        assert found_data == 1
        found_data = d.find("b")
        assert found_data == 2
        