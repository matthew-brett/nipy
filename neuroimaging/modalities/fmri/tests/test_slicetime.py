import numpy as np

from neuroimaging.modalities.fmri import slice_time

from neuroimaging.core.api import CoordinateMap, Image
from neuroimaging.modalities.fmri.api import fromimage

def test_nointerp():
    t = np.linspace(0,1,7)
    Y = np.random.standard_normal(t.shape + (11,4,5))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    f.slice_times = np.zeros(f[0].shape[0])
    f.slice_axis = 0
    ff = slice_time.slice_time(f)
    assert(np.allclose(np.asarray(ff), Y))

def test_nointerp_sinc():
    t = np.linspace(0,1,7)
    Y = np.random.standard_normal(t.shape + (11,4,5))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t)
    f.slice_axis = 0
    f.slice_times = np.zeros(f[0].shape[0])
    ff = slice_time.slice_time(f, interpolator=slice_time.sinc_interp)
    assert(np.allclose(np.asarray(ff), Y))

def test_linear():
    t = np.linspace(0,7*2.3,7)
    s = np.linspace(0.2,0.8,11)
    # Y is a collection of time-series where
    # f(t,i,j,k) = t/7 + N(i,j,k)
    Y = np.add.outer(np.linspace(0,7,7), np.random.standard_normal((11,4,5)))
    Y = Image(Y, CoordinateMap.identity(['t','z','y','x'], Y.shape))
    f = fromimage(Y, volume_start_times=t, slice_times=s)
    f.slice_axis = 0
    ff = slice_time.slice_time(f, bounds_error=False, fill_value=0.)
    # all the points of ff(:,4,:,:) should be shifted back-in-time
    # by a subsample fraction s[4]/TR -- since the temporal function is
    # a linear ramp, this shift just moves the intercept back-in-time
    A = np.asarray(ff)[3,4] + s[4]/2.3
    B = np.asarray(Y)[3,4]
    assert(np.allclose(A, B))

## import pylab as P
def test_periodic_sincinterp():
    tr = 2.3
    t = np.linspace(0,30*tr,30,endpoint=False)
    s = np.linspace(0.2,0.8,11)
    f0 = 1/(30*tr)
    tempo = np.sin(2*np.pi*f0*t)
    vol = np.random.standard_normal((11,4,5))
    Y = np.add.outer(tempo, vol)
    Y = Image(Y, CoordinateMap.identity(['t', 'z', 'y', 'x'], Y.shape))
    f = fromimage(Y, volume_start_times=t, slice_times=s)
    f.slice_axis = 0
    ff = slice_time.slice_time(f, interpolator=slice_time.sinc_interp)

    tempo_exact = np.sin(2*np.pi*f0*(t-s[4]))

    interp_sig = np.asarray(ff)[:,4,2,2]
    exact_sig = tempo_exact + vol[4,2,2]
    err_nrg = ((exact_sig - interp_sig)**2).sum()
    sig_nrg = (exact_sig**2).sum()
##     P.subplot(211)
##     P.plot(np.asarray(f)[:,4,2,2])
##     P.plot(interp_sig)
##     P.plot(exact_sig)
##     P.subplot(212)
##     P.plot(exact_sig-interp_sig)
##     P.title('normal sinc interp')
##     P.show()
    
    assert err_nrg < 0.01 * sig_nrg

def test_detrended_periodic_sincinterp():
    tr = 2.3
    t = np.linspace(0,30*tr,30,endpoint=False)
    s = np.linspace(0.2,0.8,11)
    f0 = 1/(30*tr)
    tempo = np.sin(2*np.pi*f0*t)
    vol = np.random.standard_normal((11,4,5))
    Y = np.add.outer(tempo, vol)
    Y = Image(Y, CoordinateMap.identity(['t', 'z', 'y', 'x'], Y.shape))
    f = fromimage(Y, volume_start_times=t, slice_times=s)
    f.slice_axis = 0
    ff = slice_time.slice_time(f, interpolator=slice_time.sinc_interp_detrend)

    tempo_exact = np.sin(2*np.pi*f0*(t-s[4]))

    interp_sig = np.asarray(ff)[:,4,2,2]
    exact_sig = tempo_exact + vol[4,2,2]
    err_nrg = ((exact_sig - interp_sig)**2).sum()
    sig_nrg = (exact_sig**2).sum()
##     P.subplot(211)
##     P.plot(np.asarray(f)[:,4,2,2])
##     P.plot(interp_sig)
##     P.plot(exact_sig)
##     P.subplot(212)
##     P.plot(exact_sig-interp_sig)
##     P.title('detrended sinc interp')
##     P.show()
    assert err_nrg < 0.01 * sig_nrg

def test_periodic_fastsinc():
    tr = 2.3
    t = np.linspace(0,30*tr,30,endpoint=False)
    s = np.linspace(0.2,0.8,11)
    f0 = 1/(30*tr)
    tempo = np.sin(2*np.pi*f0*t)
    vol = np.random.standard_normal((11,4,5))
    Y = np.add.outer(tempo, vol)
    Y = Image(Y, CoordinateMap.identity(['t', 'z', 'y', 'x'], Y.shape))
    f = fromimage(Y, volume_start_times=t, slice_times=s)
    f.slice_axis = 0
    ff = slice_time.slice_time(f, interpolator=slice_time.fast_sinc)

    tempo_exact = np.sin(2*np.pi*f0*(t-s[4]))

    interp_sig = np.asarray(ff)[:,4,2,2]
    exact_sig = tempo_exact + vol[4,2,2]
    err_nrg = ((exact_sig - interp_sig)**2).sum()
    sig_nrg = (exact_sig**2).sum()
    
    assert err_nrg < 0.01 * sig_nrg
