""" Wrappers for ANTS utilties
"""

from __future__ import division, absolute_import

import sys
from os import environ
from os.path import (join as pjoin, isfile, sep as psep, dirname,
                     split as psplit)
from tempfile import NamedTemporaryFile

from nipy import save_image, load_image
from ..utils.compat3 import string_types
from ..externals import sh

# ANTSPATH as specified by you, dear user
ANTSPATH = None


class AntsError(Exception):
    pass


def _likely_antspath(path):
    """ Return True if `path` likely to be good ANTSPATH """
    return isfile(pjoin(path, 'ants.sh'))


# ANTSPATH guesses key=sys.platform string, value=tuple of paths
_ANTS_GUESSES = dict(
    linux2 = ('/usr/lib/ants',), # Neurodebian default install
    darwin = ('/usr/bin',), # dmg install location
)

def find_antspath():
    """ Try to find a plausible value for ANTSPATH environment variable

    Thus far tested on:

    * OSX: ANTs-1.9.v4-Darwin.dmg installer
    * Debian wheezy: Neurodebian `apt-get install ants`

    Returns
    -------
    antspath : str
        path to ANTS utilities, with no trailing directory separator
    """
    antspath = environ.get('ANTSPATH')
    if not antspath is None:
        # Remove trailing directory separator
        while antspath.endswith(psep):
            antspath = antspath[:-1]
        return antspath
    ants_binary = sh.which('ANTS')
    if not ants_binary is None:
        antspath = dirname(ants_binary)
        if _likely_antspath(antspath):
            return antspath
    # Now we're guessing
    for guess in _ANTS_GUESSES[sys.platform]:
        if _likely_antspath(guess):
            return guess
    raise AntsError("Can't find plausible ANTSPATH - try setting ANTSPATH "
                    "environment variable")


# Cached result of search for ANTSPATH
_FOUND_ANTSPATH = None

def get_antspath():
    """ Return specified or estimated ANTSPATH value """
    if not ANTSPATH is None:
        return ANTSPATH
    global _FOUND_ANTSPATH
    if _FOUND_ANTSPATH is None:
        _FOUND_ANTSPATH = find_antspath()
    return _FOUND_ANTSPATH


def as_filename(img):
    """ Return saved image from image, or pass through if string """
    if isinstance(img, string_types):
        return img
    fobj = NamedTemporaryFile(suffix='.nii')
    save_image(img, fobj)
    return fobj.name


def make_prefixer(prefix):
    """ Make a function that prepends `prefix` to input filename """
    def add_prefix(fname):
        pth, fname = psplit(fname)
        return pjoin(pth, prefix + fname)
    return add_prefix


class N4BiasFieldCorrection(object):
    """ Class to make callable interface to N4BiasCorrection from ANTS

    Uses the parameter defaults culled from ANTS ``ants.sh``

    Use with something like::

        import nipy.testing
        n4corrector = ants.N4BiasFieldCorrection()
        in_fname = nipy.testing.anatfile # a filename
        res = n4corrector(in_fname, 'fixed.nii')

    Or with an in-memory image:

        import nipy
        in_image = nipy.load_image(in_fname)
        res = n4corrector(in_image, 'fixed.nii')
    """
    def __init__(self,
                 image_dimensionality=3,
                 shrink_factor=2,
                 mask_image=None,
                 weight_image=None,
                 convergence=((50, 50, 50, 50), 0.000001),
                 bspline_fitting=(200, 3),
                 histogram_sharpening=(0.15,0.01,200),
                 pathmaker=make_prefixer('repaired_')
                ):
        self.image_dimensionality=image_dimensionality
        self.shrink_factor=shrink_factor
        self.mask_image=mask_image
        self.weight_image=weight_image
        self.convergence=convergence
        self.bspline_fitting=bspline_fitting
        self.histogram_sharpening=histogram_sharpening
        self.pathmaker=pathmaker
        self._cmd = sh.Command(pjoin(get_antspath(), 'N4BiasFieldCorrection'))

    def _process_kwargs(self):
        # Process arguments
        kwargs = {}
        conv_iters, conv_thresh = self.convergence
        conv_iters = ['{0:g}'.format(i) for i in conv_iters]
        conv_str = "[{0},{1}]".format('x'.join(conv_iters), conv_thresh)
        kwargs['convergence'] = conv_str
        bspline_grid, bspline_order = self.bspline_fitting
        try:
            len(bspline_grid)
        except TypeError:
            pass
        else:
            bspline_grid = ['{0:g}'.format(i) for i in bspline_grid]
        bspline_str = "[{0},{1}]".format(bspline_grid, bspline_order)
        kwargs['bspline_fitting'] = bspline_str
        histogram_str = "[{0},{1},{2}]".format(*self.histogram_sharpening)
        kwargs['histogram_sharpening'] = histogram_str
        if not self.mask_image is None:
            kwargs['mask_image'] = as_filename(self.mask_image)
        if not self.weight_image is None:
            kwargs['weight_image'] = as_filename(self.weight_image)
        return kwargs

    def __call__(self, input, out_fname=None):
        in_fname = as_filename(input)
        if out_fname is None:
            out_fname = self.pathmaker
        if hasattr(out_fname, '__call__'):
            out_fname = out_fname(in_fname)
        self._cmd(i=in_fname, o=out_fname, **self._process_kwargs())
        return load_image(out_fname)
