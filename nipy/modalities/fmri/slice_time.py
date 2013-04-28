"""
This module implements some basic slice timing routines.
"""

from copy import copy

import numpy as np
from scipy.interpolate import interp1d
from scipy.special.basic import sinc

from .fmri import FmriImageList
from nipy.core.api import Image

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

    def f(x):
        y = np.dot(A, x.reshape(x.shape[0], np.product(x.shape[1:]))).reshape((A.shape[0],) + x.shape[1:])
        return y
    f.A = A
    return f


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
        yield image_list.volume_start_times + slicetimes[j], ij, ij


def fast_sinc(frac, data):
    """
    Placeholder for Mike's fast sinc interpolation function, with time axis=0.

    Inputs:
    =======
    frac : float
           Indicates the fraction of a sample to delay or advance the sequence

    data : ndarray
           The sequence(s) with time dimension on axis 0

    """
    L = data.shape[0]
    Fnyq = L/2
    ramp_rate = 2./L
    data_f = np.fft.fft(data, axis=0)
    phs_ramp = np.zeros((L,), data_f.dtype)
    phs_ramp[:Fnyq+1] = np.exp(1j*np.pi*np.arange(Fnyq+1)*frac*ramp_rate)
    if not L%2:
        phs_ramp[Fnyq+1:] = phs_ramp[1:Fnyq][::-1].conjugate()
    else:
        phs_ramp[Fnyq+1:] = phs_ramp[1:Fnyq+1][::-1].conjugate()

    phs_sl = (slice(None),) + (None,)*(len(data.shape[1:]))
    data_f *= phs_ramp[phs_sl]
    data_i = np.fft.ifft(data_f, axis=0).real
    return data_i


def detrend(interpolator):
    """ Decorator for interpolators to remove linear trends from data
    """
    def new_interpolator(input_times, data, *arg, **kw):
        # remove 1st order polynomial from data to interpolate
        a1,a0 = np.polyfit(input_times,
                           data.reshape(data.shape[0],
                                        np.product(data.shape[1:])),
                           1)
        a1.shape = a0.shape = data.shape[1:]
        trends = np.multiply.outer(input_times, a1) + a0[None]
        data -= trends
        g = interpolator(input_times, data, *arg, **kw)
        data += trends
        def f(x):
            y = g(x)
            trends = np.multiply.outer(x, a1) + a0[None]
            y += trends
            return y
        return f
    return new_interpolator


@detrend
def newinterp(input_times, data):
    return interp1d(input_times, data)


def slice_time(image_list,
               interpolator=interp1d,
               *intarg,
               **intkw):
    """ Slice time correction for an entire fMRI image.

    Returns an fMRI image where each slice of each volume is interpolated in
    time so as to appear to be acquired at the start_time for that volume.

    Parameters
    ----------
    image_list : FmriImageList
        fMRI image to be slice-timed
    interpolator : callable, optional
        Callable returning an interpolating function that can be evaluated at
        output_times.
    \*intarg : positional args, optional
        Positional arguments to interpolator
    \*\*intkw : keyword args, optional
       Keyword arguments to interpolator

    Returns
    -------
    fimg : FmriImageList
        FmriImage list with interpolated data
    """
    test = filter(lambda x: not x, [i.coordmap == image_list[0].coordmap for i in image_list]) == []
    # TODO: fix equality check of coordmaps....
    print map(lambda x: not x, [i.coordmap == image_list[0].coordmap for i in image_list]),

    generator = slice_generator(image_list, image_list.slice_times, axis=image_list.slice_axis)
    output_times = image_list.volume_start_times
    output_data = np.zeros((len(image_list),) + image_list[0].shape)
    axis_interpolator(np.asarray(image_list),
                      generator,
                      output_times,
                      output_data,
                      interpolator,
                      *intarg,
                      **intkw)
    ims = []

    for i in range(output_data.shape[0]):
        ims.append(Image(output_data[i],
                         copy(image_list[i].coordmap)))

    return FmriImageList(ims, volume_start_times=image_list.volume_start_times,
                         slice_times=np.zeros(image_list[0].shape[image_list.slice_axis]))


def axis_interpolator(image_array,
                      generator,
                      output_values,
                      output_data,
                      interpolator=interp1d,
                      *intarg,
                      **intkw):
    """
    image_array: ndarray
                Data to be interpolated along a given axis (determined by the
                generator).

    generator: generator
                  Generator that yields tuples (input_values, input_indices, output_indices)
                  where input_values are the axis values at which
                  image_array[:,input_indices] is observed. It is assumed
                  that image_array[:,input_indices].shape[0] == input_values.shape[0].
                  It is also assumed that generator has an attribute output_shape.

    output_values: np.ndarray
                  Values at which the interpolator is to
                  be evaluated.

    output_data: np.ndarray
                  Array in which to store output values.

    interpolator: callable
                  Callable returning an interpolating function that can be
                  evaluated at output_values.
                  Defaults to scipy.interpolate.interp1d.

    intarg, intkw:
                  Optional arguments to interpolator.

    Outputs:
    ========

    None. (Data is filled in to output_data above).

    """
    data = np.asarray(image_array)

    output_values = np.asarray(output_values)
    assert(len(output_values.shape) == 1)
    nout = output_values.shape[0]

    for input_values, input_indices, output_indices in generator:
        d = data[:,input_indices]
        if interpolator is not fast_sinc:
            f = make_filter(interpolator, input_values,
                            output_values, *intarg, **intkw)
            output_data[:,output_indices] = f(d)
        else:
            tr = output_values[1] - output_values[0]
            assert np.allclose(np.diff(output_values), tr), 'sinc interpolation expects equally spaced time points on output'
            assert np.allclose(np.diff(input_values), tr), 'sinc interpolation expects equally spaced time points on input'
            assert output_values.shape == input_values.shape, 'sinc interpolation requires the same number of time points on input and output'
            output_data[:,output_indices] = fast_sinc((output_values[0] - input_values[0]) / tr, d)

    return None


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

    assert np.allclose(np.diff(t), tr), 'expecting equally spaced time points on input times'

    def f(tnew):
        m = np.arange(x.shape[0])
        assert tnew.min() >= (t.min()-tr) and tnew.max() <= (t.max()+tr), 'extrapolating to points more than one sample away from original data'
        # align tnew relative to t-grid, and find sub-sample spacing
        _t = (tnew-t[0])/float(tr)
        dmt = _t[:,None] - m
        d = sinc(dmt)
        if window is not None:
            d *= window(dmt)
        return np.dot(d, x)
    return f


@detrend
def sinc_interp_detrend(t, x, window=None):
    return sinc_interp(t, x, window=window)
