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

    def f(x):
        return np.dot(A, x.reshape(x.shape[0], np.product(x.shape[1:]))).reshape((A.shape[0], np.product(x.shape[1:])))
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

    data : ndarray

    """
    pass


def detrend(interpolator):
    def new_interpolator(input_times, data, *arg, **kw):
        g = interpolator(input_times, data, *arg, **kw)
        def f(x):
            xmu = np.mean(x, axis=0)
            y = g(x - np.multiply.outer(np.ones(x.shape[0]), xmu))
            return y + xmu
        return f

@detrend
def newinterp(input_times, data):
    return interp1d(input_times, data)

def slice_time(image_list,
               interpolator=interp1d,
               *intarg,
               **intkw):
    """

    Slice time correction for an entire fMRI image.
    Returns an fMRI image where each slice of each volume is interpolated
    in time so as to appear to be acquired at the start_time for that volume.

    Inputs:
    =======
    image_list: FmriImageList
                fMRI image to be slice-timed
              
    interpolator: callable
                  Callable returning an interpolating function that can be
                  evaluated at output_times.

    intarg, intkw: 
                  Optional arguments to interpolator

    """

    assert filter(lambda x: not x, [i.coordmap == image_list[0].coordmap for i in image_list]) == [], 'slice_time expecting all volumes to have the same coordmap'
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
        ims.append(Image(output_data[i], image_list[i].coordmap.copy()))
    
    return FmriImageList(ims, volume_start_times=image_list.volume_start_times,
                         slice_times=np.zeros(image_list.shape[image_list.slice_axis]))

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
        if interpolator is not fast_sinc:
            d = data[:,input_indices]
            f = make_filter(interpolator, input_values, 
                            output_values, *intarg, **intkw)
            output_data[:,output_indices] = f(d)
        else:
            tr = output_values[1] - output_values[0]
            assert np.allclose(np.diff(output_values), tr), 'sinc interpolation expects equally spaced time points on output'
            assert np.allclose(np.diff(input_values), tr), 'sinc interpolation expects equally spaced time points on input'
            assert np.allclose(output_values.shape == input_values.shape), 'sinc interpolation requires the same number of time points on input and output'
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

