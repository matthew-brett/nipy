import numpy as np

from neuroimaging.modalities.fmri import slice_time

from neuroimaging.core.api import CoordinateMap, Image
from neuroimaging.modalities.fmri.api import fromimage

def test_nointerp():
    t = np.linspace(0,1,7)
    Y = np.random.standard_normal(t.shape + (11,4,5))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    g = slice_time.slice_generator(f, np.zeros(Y.shape[1]))
    ff = slice_time.slice_time(f, g)
    assert(np.allclose(np.asarray(ff), Y))

def test_nointerp_sinc():
    t = np.linspace(0,1,7)
    Y = np.random.standard_normal(t.shape + (11,4,5))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    g = slice_time.slice_generator(f, np.zeros(t.shape))
    ff = slice_time.slice_time(f, g, interpolator=slice_time.sinc_interp)
    assert(np.allclose(np.asarray(ff), Y))

def test_nointerp_sinc():
    t = np.linspace(0,7,7)
    s = np.linspace(0.2,0.8,5)
    Y = np.multiply.outer(t, np.ones((5,4,5)))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    g = slice_time.slice_generator(f, s)
    ff = slice_time.slice_time(f, g, bounds_error=False, fill_value=0.)
    assert(np.allclose(np.asarray(ff)[3,4] + s[3], np.asarray(Y)[3,4]))


