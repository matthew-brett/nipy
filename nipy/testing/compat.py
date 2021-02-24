""" Compatibility functions for nose -> pytest conversion.
"""

import pytest


from unittest.case import SkipTest


def assert_equal(a, b):
    assert a == b


def assert_not_equal(a, b):
    assert a != b


def assert_true(a):
    assert a


def assert_false(a):
    assert not a


def assert_raises(E, callable, *args, **kwargs):
    with pytest.raises(E):
        callable(*args, **kwargs)
