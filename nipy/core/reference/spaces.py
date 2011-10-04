""" Useful neuroimaging coordinate map makers and utilities """

import numpy as np

from .coordinate_system import CoordSysMaker
from .coordinate_map import CoordMapMaker
from ..transforms.affines import from_matrix_vector


class XYZSpace(object):
    """ Class contains logic for spaces with XYZ coordinate systems

    >>> sp = XYZSpace('hijo')
    >>> print sp
    hijo: [('x', 'hijo-x=L->R'), ('y', 'hijo-y=P->A'), ('z', 'hijo-z=I->S')]
    >>> csm = sp.to_coordsys_maker()
    >>> cs = csm(3)
    >>> cs
    CoordinateSystem(coord_names=('hijo-x=L->R', 'hijo-y=P->A', 'hijo-z=I->S'), name='hijo', coord_dtype=float64)
    >>> cs in sp
    True
    """
    x_suffix = 'x=L->R'
    y_suffix = 'y=P->A'
    z_suffix = 'z=I->S'

    def __init__(self, name):
        self.name = name

    @property
    def x(self):
        """ x-space coordinate name """
        return "%s-%s" % (self.name, self.x_suffix)

    @property
    def y(self):
        """ y-space coordinate name """
        return "%s-%s" % (self.name, self.y_suffix)

    @property
    def z(self):
        """ z-space coordinate name """
        return "%s-%s" % (self.name, self.z_suffix)

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.name)

    def __str__(self):
        return "%s: %s" % (self.name, sorted(self.as_map().items()))

    def __eq__(self, other):
        """ Equality defined as having the same xyz names """
        try:
            otuple = other.as_tuple()
        except AttributeError:
            return False
        return self.as_tuple() == otuple

    def __ne__(self, other):
        return not self == other

    def as_tuple(self):
        """ Return xyz names as tuple

        >>> sp = XYZSpace('hijo')
        >>> sp.as_tuple()
        ('hijo-x=L->R', 'hijo-y=P->A', 'hijo-z=I->S')
        """
        return self.x, self.y, self.z

    def as_map(self):
        """ Return xyz names as dictionary

        >>> sp = XYZSpace('hijo')
        >>> sorted(sp.as_map().items())
        [('x', 'hijo-x=L->R'), ('y', 'hijo-y=P->A'), ('z', 'hijo-z=I->S')]
        """
        return dict(zip('xyz', self.as_tuple()))

    def register_to(self, mapping):
        """ Update `mapping` with key=self.x, value='x' etc pairs

        Note that this is the opposite way round for keys, values, compared to
        the ``as_map`` method.

        Parameters
        ----------
        mapping : mapping
            such as a dict

        Returns
        -------
        None

        Examples
        --------
        >>> sp = XYZSpace('hijo')
        >>> mapping = {}
        >>> sp.register_to(mapping)
        >>> sorted(mapping.items())
        [('hijo-x=L->R', 'x'), ('hijo-y=P->A', 'y'), ('hijo-z=I->S', 'z')]
        """
        mapping.update(dict(zip(self.as_tuple(), 'xyz')))

    def to_coordsys_maker(self, extras=()):
        """ Make a coordinate system maker for this space

        Parameters
        ----------
        extra : sequence
            names for any further axes after x, y, z

        Returns
        -------
        csm : CoordinateSystemMaker

        Examples
        --------
        >>> sp = XYZSpace('hijo')
        >>> csm = sp.to_coordsys_maker()
        >>> csm(3)
        CoordinateSystem(coord_names=('hijo-x=L->R', 'hijo-y=P->A', 'hijo-z=I->S'), name='hijo', coord_dtype=float64)
        """
        return CoordSysMaker(self.as_tuple() + tuple(extras), name=self.name)

    def __contains__(self, obj):
        """ True if `obj` can be thought of as being 'in' this space

        We define `obj` as being in our space, if the first 3 coordinate system
        names are the same as ours.  A coordinate system can be in our space, as
        can a coordinate map (we test the function_range), or an image (we test
        the coordmap of the image).

        Parameters
        ----------
        obj : object
            Usually a coordinate system, a coordinate map, or an Image (with a
            ``coordmap`` attribute

        Returns
        -------
        tf : bool
            True if `obj` is 'in' this space

        Examples
        --------
        >>> from nipy.core.api import Image, AffineTransform, CoordinateSystem
        >>> sp = XYZSpace('hijo')
        >>> names = sp.as_tuple()
        >>> cs = CoordinateSystem(names)
        >>> cs in sp
        True
        >>> cs = CoordinateSystem(names + ('another_name',))
        >>> cs in sp
        True
        >>> cmap = AffineTransform('ijk', names, np.eye(4))
        >>> cmap in sp
        True
        >>> img = Image(np.zeros((3,4,5)), cmap)
        >>> img in sp
        True
        """
        try:
            obj = obj.coordmap
        except AttributeError:
            pass
        try:
            obj = obj.function_range
        except AttributeError:
            pass
        my_names = self.as_tuple()
        ndim = len(my_names)
        if obj.ndim < ndim:
            return False
        return obj.coord_names[:ndim] == my_names


# Generic coordinate map maker for voxels (function_domain)
voxel_cs = CoordSysMaker('ijklmnop', 'array')

# Module level mapping from key=name to values in 'x' or 'y' or 'z'
known_names = {}
known_spaces = []

# Standard spaces defined
for _name in ('unknown', 'scanner', 'aligned', 'mni', 'talairach'):
    _space = XYZSpace(_name)
    known_spaces.append(_space)
    _space.register_to(known_names)
    _csm = _space.to_coordsys_maker('t')
    _cmm = CoordMapMaker(voxel_cs, _csm)
    # Put these into the module namespace
    exec('%s_space = _space' % _name)
    exec('%s_csm = _csm' % _name)
    exec('vox2%s = _cmm' % _name)


def known_space(obj, spaces=None):
    """ If `obj` is in a known space, return the space, otherwise return None

    Parameters
    ----------
    obj : object
        Object that can be tested against an XYZSpace with ``obj in sp``
    spaces : None or sequence, optional
        spaces to test against.  If None, use the module level ``known_spaces``
        list to test against.

    Returns
    -------
    sp : None or XYZSpace
        If `obj` is not in any of the `known_spaces`, return None.  Otherwise
        return the first matching space in `known_spaces`

    Examples
    --------
    >>> from nipy.core.api import CoordinateSystem
    >>> sp0 = XYZSpace('hijo')
    >>> sp1 = XYZSpace('hija')

    Make a matching coordinate system

    >>> cs = sp0.to_coordsys_maker()(3)

    Test

    >>> known_space(cs, (sp0, sp1))
    XYZSpace('hijo')
    >>> known_space(CoordinateSystem('xyz'), (sp0, sp1)) is None
    True
    """
    if spaces is None:
        # use module level global
        spaces = known_spaces
    for sp in spaces:
        if obj in sp:
            return sp
    return None


class SpaceError(Exception):
    pass

class SpaceTypeError(SpaceError):
    pass

class AxesError(SpaceError):
    pass

class AffineError(SpaceError):
    pass

def xyz_affine(coordmap, name2xyz=None):
    """ Return voxel to XYZ affine for `coordmap`

    Parameters
    ----------
    coordmap : ``CoordinateMap`` instance
    name2xyz : None or mapping, optional
        Object such that ``name2xyz[ax_name]`` returns 'x', or 'y' or 'z' or
        raises a KeyError for a str ``ax_name``.  None means use module default.

    Returns
    -------
    xyz_aff : (4,4) array
        voxel to X, Y, Z affine mapping

    Raises
    ------
    SpaceTypeError : if this is not an affine coordinate map
    AxesError : if not all of x, y, z recognized in `coordmap` range
    AffineError : if axes dropped from the affine contribute to x, y, z
    coordinates

    Examples
    --------
    >>> cmap = vox2mni(np.diag([2,3,4,5,1]))
    >>> cmap
    AffineTransform(
       function_domain=CoordinateSystem(coord_names=('i', 'j', 'k', 'l'), name='array', coord_dtype=float64),
       function_range=CoordinateSystem(coord_names=('mni-x=L->R', 'mni-y=P->A', 'mni-z=I->S', 't'), name='mni', coord_dtype=float64),
       affine=array([[ 2.,  0.,  0.,  0.,  0.],
                     [ 0.,  3.,  0.,  0.,  0.],
                     [ 0.,  0.,  4.,  0.,  0.],
                     [ 0.,  0.,  0.,  5.,  0.],
                     [ 0.,  0.,  0.,  0.,  1.]])
    )
    >>> xyz_affine(cmap)
    array([[ 2.,  0.,  0.,  0.],
           [ 0.,  3.,  0.,  0.],
           [ 0.,  0.,  4.,  0.],
           [ 0.,  0.,  0.,  1.]])
    """
    if name2xyz is None:
        name2xyz = known_names
    try:
        affine = coordmap.affine
    except AttributeError:
        raise SpaceTypeError('Need affine coordinate map')
    order = xyz_order(coordmap.function_range, name2xyz)
    affine = affine[order[:3]]
    # Check that dropped dimensions don't provide xyz coordinate info
    extra_cols = affine[:,3:-1]
    if not np.allclose(extra_cols, 0):
        raise AffineError('Dropped dimensions not orthogonal to xyz')
    return from_matrix_vector(affine[:3,:3], affine[:3,-1])


def xyz_order(coordsys, name2xyz=None):
    """ Vector of orders for sorting coordsys axes in xyz first order

    Parameters
    ----------
    coordsys : ``CoordinateSystem`` instance
    name2xyz : None or mapping, optional
        Object such that ``name2xyz[ax_name]`` returns 'x', or 'y' or 'z' or
        raises a KeyError for a str ``ax_name``.  None means use module default.

    Returns
    -------
    xyz_order : list
        Ordering of axes to get xyz first ordering.  See the examples.

    Raises
    ------
    AxesError : if there are not all of x, y and z axes

    Examples
    --------
    >>> from nipy.core.api import CoordinateSystem
    >>> xyzt_cs = mni_csm(4) # coordsys with t (time) last
    >>> xyzt_cs
    CoordinateSystem(coord_names=('mni-x=L->R', 'mni-y=P->A', 'mni-z=I->S', 't'), name='mni', coord_dtype=float64)
    >>> xyz_order(xyzt_cs)
    [0, 1, 2, 3]
    >>> tzyx_cs = CoordinateSystem(xyzt_cs.coord_names[::-1], 'reversed')
    >>> tzyx_cs
    CoordinateSystem(coord_names=('t', 'mni-z=I->S', 'mni-y=P->A', 'mni-x=L->R'), name='reversed', coord_dtype=float64)
    >>> xyz_order(tzyx_cs)
    [3, 2, 1, 0]
    """
    if name2xyz is None:
        name2xyz = known_names
    names = coordsys.coord_names
    N = len(names)
    axvals = np.zeros(N, dtype=int)
    for i, name in enumerate(names):
        try:
            xyz_char = name2xyz[name]
        except KeyError:
            axvals[i] = N+i
        else:
            axvals[i] = 'xyz'.index(xyz_char)
    if not set(axvals).issuperset(range(3)):
        raise AxesError("Not all of x, y, z recognized in coordinate map")
    return list(np.argsort(axvals))


def is_xyz_affable(coordmap, name2xyz=None):
    """ Return True if the coordap has an xyz affine

    Parameters
    ----------
    coordmap : ``CoordinateMap`` instance
        Coordinate map to test
    name2xyz : None or mapping, optional
        Object such that ``name2xyz[ax_name]`` returns 'x', or 'y' or 'z' or
        raises a KeyError for a str ``ax_name``.  None means use module default.

    Returns
    -------
    tf : bool
        True if `coordmap` has an xyz affine, False otherwise

    Examples
    --------
    >>> cmap = vox2mni(np.diag([2,3,4,5,1]))
    >>> cmap
    AffineTransform(
       function_domain=CoordinateSystem(coord_names=('i', 'j', 'k', 'l'), name='array', coord_dtype=float64),
       function_range=CoordinateSystem(coord_names=('mni-x=L->R', 'mni-y=P->A', 'mni-z=I->S', 't'), name='mni', coord_dtype=float64),
       affine=array([[ 2.,  0.,  0.,  0.,  0.],
                     [ 0.,  3.,  0.,  0.,  0.],
                     [ 0.,  0.,  4.,  0.,  0.],
                     [ 0.,  0.,  0.,  5.,  0.],
                     [ 0.,  0.,  0.,  0.,  1.]])
    )
    >>> is_xyz_affable(cmap)
    True
    >>> time0_cmap = cmap.reordered_domain([3,0,1,2])
    >>> time0_cmap
    AffineTransform(
       function_domain=CoordinateSystem(coord_names=('l', 'i', 'j', 'k'), name='array', coord_dtype=float64),
       function_range=CoordinateSystem(coord_names=('mni-x=L->R', 'mni-y=P->A', 'mni-z=I->S', 't'), name='mni', coord_dtype=float64),
       affine=array([[ 0.,  2.,  0.,  0.,  0.],
                     [ 0.,  0.,  3.,  0.,  0.],
                     [ 0.,  0.,  0.,  4.,  0.],
                     [ 5.,  0.,  0.,  0.,  0.],
                     [ 0.,  0.,  0.,  0.,  1.]])
    )
    >>> is_xyz_affable(time0_cmap)
    False
    """
    try:
        xyz_affine(coordmap, name2xyz)
    except SpaceError:
        return False
    return True
