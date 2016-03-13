""" Collection of utility functions and classes

Some of these come from the matplotlib ``cbook`` module with thanks.
"""

from operator import mul
from functools import reduce


def pyprod(seq, initial=1):
    """ Pure Python implementation of product

    This is likely faster than `np.prod` for small sequences, and returns an
    integer for an integer sequence.

    Parameters
    ----------
    seq : iterable
        Sequence of values
    initial : object, optional
        Initial value.  Default is 1.

    Returns
    -------
    prod : object
        Result of multiplying each element in sequence
    """
    return reduce(mul, seq, initial)


def is_iterable(obj):
    """ Return True if `obj` is iterable
    """
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_numlike(obj):
    """ Return True if `obj` looks like a number
    """
    try:
        obj + 1
    except:
        return False
    return True
