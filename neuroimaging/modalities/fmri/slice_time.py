"""
This module implements some basic slice timing routines.
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.special.basic import sinc

from fmri import fromimage, FmriImageList

def make_filter(interpolator, input_times, output_times,
                *intarg, **intkw):
    """
    Create linear filter A representing a linear interpolator.

    interpolator(input_times, Y, *intarg, **intkw)(output_times) = np.dot(A, Y)

    Inputs:
    =======

    interpolator: callable
                  Callable returning an interpolating function that can be
                  evaluated at output_times.

    input_times: np.ndarray
                  Time points at which the data is observed.

    output_times: np.ndarray
                  Time points at which the interpolator is to
                  be evaluated.

    intarg, intkw: 
                  Optional arguments to interpolator
    """

    input_times = np.asarray(input_times)
    assert(len(input_times.shape) == 1)
    nin = input_times.shape[0]

    output_times = np.asarray(output_times)
    assert(len(output_times.shape) == 1)
    nout = output_times.shape[0]

    A = np.zeros((nout, nin))
    I = np.identity(nin)

    for i in range(nin):
        A[:,i] = interpolator(input_times, I[:,i], *intarg, **intkw)(output_times)
    return A

def slice_generator(image_list, slicetimes, axis=0):
    """
    A generator, given an array of slicetimes along a given axis
    of an fMRI volume, yield appropriate values
    for use in slice_time.

    It is assumed that the shape of each element of image_list is the
    same.
    """

    shape = image_list[0].shape

    for j in range(shape[axis]):
        ij = (slice(None,None,None),)*axis + (slice(j,j+1),)
        if len(ij) == 1:
            ij = ij[0]
        yield image_list.volume_start_times + slicetimes[j], ij


def slice_time(image_list,
               generator,
               output_times=None,
               interpolator=interp1d,
               *intarg,
               **intkw):
    """

    image_list: FmriImageList
                  fMRI image to be slice-timed.

    generator: generator
                  Generator that yields tuples (input_times, indices)
                  where input_times are the 'experiment times' at which
                  image_list[:,indices] is observed.

    output_times: np.ndarray
                  Time points at which the interpolator is to
                  be evaluated. Defaults to image_list.volume_start_times.

    interpolator: callable
                  Callable returning an interpolating function that can be
                  evaluated at output_times. 
                  Defaults to scipy.interpolate.interp1d.

    intarg, intkw: 
                  Optional arguments to interpolator.

    """

    data = np.asarray(image_list)

    if output_times is None:
        output_times = image_list.volume_start_times

    output_times = np.asarray(output_times)
    assert(len(output_times.shape) == 1)
    nout = output_times.shape[0]

    output_data = np.zeros((nout,) + data.shape[1:])
    
    for input_times, where in generator:
        A = make_filter(interpolator, input_times, 
                        output_times, *intarg, **intkw)
        d = data[:,where]
        oshape = d.shape
        d.shape = (d.shape[0], np.product(d.shape[1:]))
        nd = np.dot(A, d)
        nd.shape = (nd.shape[0],) + oshape[1:]
        output_data[:,where] = nd

    return output_data

def sinc_interp(t, x, window=None):
    """
    Return a function that can evaluate the 
    sinc-interpolated signal x, observed at t. 
    The time points t are supposed to be equally spaced,
    otherwise an exception is raised. 

    Note: A copy of x is made, so subsequent modifications
          of x does not affect the interpolator.
    """

    x = np.asarray(x).copy()
    tr = t[1]-t[0]
    
    assert np.allclose(t[1:]-t[:-1], tr), 'expecting equally spaced time points'

    def f(tnew):
        m = np.arange(x.shape[0])
        _t = tnew / float(tr)
        dmt = np.subtract.outer(m, _t)
        d = sinc(dmt)
        if window is not None:
            d *= window(dmt)
        return np.dot(x.T, d).T
    return f

