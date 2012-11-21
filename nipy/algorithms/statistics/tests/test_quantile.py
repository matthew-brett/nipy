#!/usr/bin/env python

import numpy as np
from numpy import median as np_median

from scipy.stats import scoreatpercentile as sp_percentile

from .._quantile import _quantile, _median

from numpy.testing import (assert_array_equal,
                           assert_array_almost_equal)


NUMERIC_TYPES = sum([np.sctypes[t]
                     for t in ('int', 'uint', 'float', 'complex')],
                    [])


def another_percentile(arr, pct, axis):
    arr = np.asarray(arr)
    if axis is None:
        arr = arr.ravel()
    if arr.ndim == 1:
        return sp_percentile(arr, pct)
    r_arr = np.rollaxis(arr, axis)
    out = np.zeros(arr.shape[1:])
    for i, vec in enumerate(r_arr):
        out[i] = sp_percentile(vec, pct)
    return out


def test_median():
    for dtype in NUMERIC_TYPES:
        for shape in ((10,), (10, 11), (10, 11, 12)):
            X = (100 * (np.random.random(shape) - .5)).astype(dtype)
            for a in range(X.ndim):
                assert_array_equal(_median(X, axis=a).squeeze(),
                                   np_median(X.astype(np.float64), axis=a))


def test_quantile():
    for dtype in NUMERIC_TYPES:
        for shape in ((10,), (10, 11), (10, 11, 12)):
            X = (100 * (np.random.random(shape) - .5)).astype(dtype)
            for a in range(X.ndim):
                assert_array_almost_equal(
                    _quantile(X, .75, axis=a, interp=True).squeeze(),
                    another_percentile(X, 75, axis=a))


if __name__ == "__main__":
    import nose
    nose.run(argv=['', __file__])
