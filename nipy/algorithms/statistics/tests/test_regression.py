""" Tests for regression module
"""

import numpy as np

from nipy.fixes.scipy.stats.models.regression import OLSModel

from ..regression import output_T, output_F, AREstimator

from nose.tools import assert_true, assert_equal, assert_raises

from numpy.testing import (assert_array_almost_equal,
                           assert_array_equal)


N = 10
X = np.c_[np.linspace(-1,1,N), np.ones((N,))]
RNG = np.random.RandomState(20110901)
Y = RNG.normal(size=(10,1)) * 10 + 100
MODEL = OLSModel(X)
RESULTS = MODEL.fit(Y)
C1 = [1, 0]


def test_model():
    # Check basics about the model fit
    # Check we fit the mean
    assert_array_almost_equal(RESULTS.theta[1], np.mean(Y))


def test_output_T():
    # Check we get required outputs
    res = RESULTS.Tcontrast(C1) # all return values
    # default is all return values
    assert_array_almost_equal([res.effect, res.sd, res.t],
                              output_T(C1, RESULTS))
    assert_array_almost_equal([res.effect, res.sd, res.t],
                              output_T(C1, RESULTS, ('effect', 'sd', 't')))
    # Input order determines return order
    assert_array_almost_equal([res.t, res.effect, res.sd],
                              output_T(C1, RESULTS, ('t', 'effect', 'sd')))
    # And can select inputs
    assert_array_almost_equal([res.t],
                              output_T(C1, RESULTS, ('t',)))
    assert_array_almost_equal([res.sd],
                              output_T(C1, RESULTS, ('sd',)))
    assert_array_almost_equal([res.effect],
                              output_T(C1, RESULTS, ('effect',)))


def test_output_F():
    # Test output_F convenience function
    rng = np.random.RandomState(ord('F'))
    Y = rng.normal(size=(10,1)) * 10 + 100
    X = np.c_[rng.normal(size=(10,3)), np.ones((N,))]
    c1 = np.zeros((X.shape[1],))
    c1[0] = 1
    model = OLSModel(X)
    results = model.fit(Y)
    # Check we get required outputs
    exp_f = results.t(0) **2
    assert_array_almost_equal(exp_f, output_F(c1, results))


def test_ar_estimator():
    # More or less a smoke test
    are = AREstimator(MODEL,2)
    rhos = are(RESULTS)
    assert_equal(len(rhos), 2)



