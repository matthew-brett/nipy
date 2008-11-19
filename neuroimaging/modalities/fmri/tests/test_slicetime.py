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
    g = slice_time.slice_generator(f, np.zeros(Y.shape[1]))
    ff = slice_time.slice_time(f, g, interpolator=slice_time.sinc_interp)
    assert(np.allclose(np.asarray(ff), Y))

def test_linear():
    t = np.linspace(0,7*2.3,7)
    s = np.linspace(0.2,0.8,11)
    Y = np.add.outer(np.linspace(0,7,7), np.random.standard_normal((11,4,5)))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    g = slice_time.slice_generator(f, s)
    ff = slice_time.slice_time(f, g, bounds_error=False, fill_value=0.)
    A = np.asarray(ff)[3,4] + s[4]/2.3
    B = np.asarray(Y)[3,4]
    assert(np.allclose(A, B))


