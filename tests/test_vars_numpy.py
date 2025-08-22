"""Unittests for vals module."""

import numpy as np
from numpy.testing import assert_array_equal

from varmeta.vals import Val, ValDict
from varmeta.vars import Var


class TestVar:
    def test_numpy_unpack_axis_default(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y", "z"),
        )
        data = np.array([[10, 11], [20, 21], [30, 31]])
        packed_vars, packed_data = force.unpack(data)
        print(packed_vars)
        print(packed_data)
        assert len(packed_data) == 3
        assert_array_equal(packed_data[0], np.array([10, 11]))
        assert packed_vars[0].name == "force x"
        assert_array_equal(packed_data[1], np.array([20, 21]))
        assert packed_vars[1].name == "force y"
        assert_array_equal(packed_data[2], np.array([30, 31]))
        assert packed_vars[2].name == "force z"

    def test_numpy_unpack_axis_1(self):
        force = Var(
            key="F",
            name="force",
            units="N",
            desciption="A force",
            components=("x", "y"),
            component_axis=1
        )
        data = np.array([[10, 11], [20, 21], [30, 31]])
        packed_vars, packed_data = force.unpack(data)
        print(packed_vars)
        print(packed_data)
        assert len(packed_data) == 2
        assert_array_equal(packed_data[0], np.array([10, 20, 30]))
        assert packed_vars[0].name == "force x"
        assert_array_equal(packed_data[1], np.array([11, 21, 31]))
        assert packed_vars[1].name == "force y"

