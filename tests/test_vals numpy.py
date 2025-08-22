"""Unittests for vals module."""

import numpy as np
from numpy.testing import assert_array_equal

from varmeta.vals import Val, ValDict
from varmeta.vars import Var


class TestVal:
    def test_numpy_unpack(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        val1 = Val(data=np.array([[10, 11], [20, 21], [30, 31]]), var=force)
        print(val1.data)
        unpacked_vals = val1.unpack()
        assert len(unpacked_vals) == 3
        assert_array_equal(unpacked_vals[0].data, np.array([10, 11]))
        assert unpacked_vals[0].var.name == "force x"
        assert_array_equal(unpacked_vals[1].data, np.array([20, 21]))
        assert unpacked_vals[1].var.name == "force y"
        assert_array_equal(unpacked_vals[2].data, np.array([30, 31]))
        assert unpacked_vals[2].var.name == "force z"


class TestValDict:
    def test_numpy_unpack(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        data = np.array([[10, 11], [20, 21], [30, 31]])
        dct = {}
        dct[force] = data
        dct = ValDict(dct)
        print(dct)

        unpacked_dct = dct.unpack()
        print(unpacked_dct)
        print('key_index', unpacked_dct._key_index)
        print(unpacked_dct.get("F_x"))
        assert len(unpacked_dct) == 3
        assert_array_equal(unpacked_dct.find('F_x'), np.array([10, 11]))
        assert unpacked_dct.find_var('F_x').name == "force x"
        assert_array_equal(unpacked_dct.find('F_y'), np.array([20, 21]))
        assert unpacked_dct.find_var('F_y').name == "force y"
        assert_array_equal(unpacked_dct.find('F_z'), np.array([30, 31]))
        assert unpacked_dct.find_var('F_z').name == "force z"

