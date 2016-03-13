""" Testing utilities module
"""
from __future__ import absolute_import

import numpy as np

from ..utilities import pyprod, is_iterable, is_numlike

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)
from numpy.testing import assert_almost_equal


def test_pyprod():
    # Python implementation of product
    assert_equal(pyprod([3, 2, 1]), 6)
    assert_equal(pyprod([-3, 2, 1]), -6)
    assert_almost_equal(pyprod([-3, 2, 1], 2.2), -13.2)
    assert_equal(pyprod([]), 1)
    assert_equal(pyprod([], 2.0), 2)
    assert_raises(TypeError, pyprod, ['a', 'b', 'c'])


def test_is_iterable():
    assert_true(is_iterable(()))
    assert_true(is_iterable([]))
    assert_true(is_iterable(np.zeros(1)))
    assert_true(is_iterable(np.zeros((1, 1))))
    assert_true(is_iterable(''))
    assert_false(is_iterable(0))
    assert_false(is_iterable(object()))

    def gen():
        yield 1

    assert_true(is_iterable(gen()))

    def func():
        return 1

    assert_false(is_iterable(func))

    class C:
        def __iter__(self):
            return self

        def __next__(self):
            return self

    assert_true(is_iterable(C()))


def test_is_numlike():
    for good in (1, 0, 1.1, False, True, np.zeros(1), np.zeros((3,)),
                 1j, np.complex128(1)):
        assert_true(is_numlike(good))
    for bad in ('', object(), np.array(''), [], [1], (), (1,)):
        assert_false(is_numlike(bad))
